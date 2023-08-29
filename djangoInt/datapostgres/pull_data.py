from djangoInt.datapostgres.postgres_connection import create_connection
import datapane as dp
import pandas as pd
from sqlalchemy import create_engine, text


engine = create_connection()

# def generate_transaction_report(start_date, end_date, t_name, engine):
#     # Define the query to fetch data
#     query_text = f"SELECT * FROM fetch_data('{start_date}', '{end_date}', '{t_name}')"
#     query = text(query_text)
#
#     # Execute the query and fetch the data into a DataFrame
#     with engine.connect() as connection:
#         result = connection.execute(query)
#         df = pd.DataFrame(result.fetchall(), columns=result.keys())
#
#     # Create a Datapane report
#     report = dp.Report(
#         dp.Table(df)
#     )
#
#     # Publish the report and get the URL
#     report_url = report.publish(name='All Transactions', open=False)
#
#     return report_url


def fetch_data(start_date, end_date, t_name):
    query = f"SELECT * FROM fetch_data('{start_date}', '{end_date}', '{t_name}')"
    df = pd.read_sql_query(query, engine)
    return df


def transactions_history(df):
    # Select only the desired columns
    columns_to_keep = ['date', 'account', 'debit', 'credit', 'payee', 'category_account']
    filtered_df = df[columns_to_keep]
    return filtered_df

def fetch_summary(df):
    # Group by 'account' and calculate the total debit and credit for each account
    dfpl = df.groupby('account').agg(
        category_account=pd.NamedAgg(column='category_account', aggfunc='first'),
        total_debit=pd.NamedAgg(column='debit', aggfunc='sum'),
        total_credit=pd.NamedAgg(column='credit', aggfunc='sum')
    ).reset_index()

    # Calculate the difference for each account
    for index, row in dfpl.iterrows():
        if row['total_debit'] > row['total_credit']:
            dfpl.at[index, 'total_debit'] = row['total_debit'] - row['total_credit']
            dfpl.at[index, 'total_credit'] = 0
        else:
            dfpl.at[index, 'total_credit'] = row['total_credit'] - row['total_debit']
            dfpl.at[index, 'total_debit'] = 0

    # Return the modified DataFrame
    return dfpl


def process_profit_and_loss(df, company_name="Your Company Name", start_date="Start Date", end_date="End Date"):
    # Calculate the amount for each row
    df['amount'] = df.apply(
        lambda row: (row['debit'] - row['credit']) if row['category_account'] in ["Expense", "COGS", "Other Expense"]
        else (row['credit'] - row['debit']),
        axis=1
    )

    # Group by category_account and account, and sum the amounts
    grouped = df.groupby(['category_account', 'account']).agg(
        amount=pd.NamedAgg(column='amount', aggfunc='sum')
    ).reset_index()

    # Separate income and expenses
    income = grouped[grouped['category_account'] == 'Revenue']
    cogs = grouped[grouped['category_account'] == 'COGS']
    expenses = grouped[grouped['category_account'] == 'Expense']
    other_income = grouped[grouped['category_account'] == 'Other Income']
    other_expense = grouped[grouped['category_account'] == 'Other Expense']

    # Convert to the desired JSON structure
    result = {
        "company_name": company_name,
        "accounting_method": "Cash Basis",
        "start_date": start_date,
        "end_date": end_date,
        "income": income.apply(
            lambda row: {"category": "Operating Income", "description": row['account'], "amount": row['amount']}, axis=1
        ).tolist(),
        "cogs": cogs.apply(
            lambda row: {"category": "Cost of Goods Sold", "description": row['account'], "amount": row['amount']},
            axis=1
        ).tolist(),

        "expenses": expenses.apply(
            lambda row: {"category": "Operating Expenses", "description": row['account'], "amount": row['amount']},
            axis=1
        ).tolist(),
        "other_income": other_income.apply(
            lambda row: {"category": "Other Income", "description": row['account'], "amount": row['amount']}, axis=1
        ).tolist(),
        "other_expense": other_expense.apply(
            lambda row: {"category": "Other Expense", "description": row['account'], "amount": row['amount']}, axis=1
        ).tolist()
    }

    return result

def fetch_bl_data(end_date, table_name):
    query = f"""SELECT account, category_account, SUM(debit) AS debit, SUM(credit) AS credit FROM {table_name} WHERE date <= '{end_date}' GROUP BY account, category_account"""
    df_bl = pd.read_sql_query(query, engine)
    return df_bl

def fetch_bl_equity(end_date, t_name):
    query = f"SELECT * FROM fetch_bl_data('{end_date}', '{t_name}')"
    df_equity = pd.read_sql_query(query, engine)
    return df_equity

def calculate_summary_or_retained_earnings(df_equity, end_date):
    # Parse the end_date to a datetime object
    end_date = pd.to_datetime(end_date)

    # Determine the closest year-end date to the given end_date
    closest_year_end = pd.Timestamp(year=end_date.year, month=12, day=31)
    if end_date.month < 12 or (end_date.month == 12 and end_date.day < 31):
        closest_year_end -= pd.DateOffset(years=1)
    # Convert the 'date' column to Pandas Timestamp objects
    df_equity['date'] = pd.to_datetime(df_equity['date'])
    # Filter the DataFrame to include only rows up to the cutoff date
    df_filtered  = df_equity[df_equity['date'] <= closest_year_end]
    df_filtered1 = df_equity[df_equity['date'] > closest_year_end]
    # Calculate net income (total revenue - total expenses) for the filtered data
    revenue = df_filtered[df_filtered['category_account'] == 'Revenue']
    cogs = df_filtered[df_filtered['category_account'] == 'COGS']
    expense = df_filtered[df_filtered['category_account'] == 'Expense']
    other_income = df_filtered[df_filtered['category_account'] == 'Other Income']
    other_expense = df_filtered[df_filtered['category_account'] == 'Other Expense']
    
    retained_earnings = revenue['credit'].sum() - revenue['debit'].sum() + expense['credit'].sum() - expense['debit'].sum()+ other_income['credit'].sum() - other_income['debit'].sum() + other_expense['credit'].sum() - other_expense['debit'].sum()- cogs['debit'].sum() + cogs['credit'].sum()
    revenue1 = df_filtered1[df_filtered1['category_account'] == 'Revenue']
    cogs1 = df_filtered1[df_filtered1['category_account'] == 'COGS']
    expense1 = df_filtered1[df_filtered1['category_account'] == 'Expense']
    other_income1 = df_filtered1[df_filtered1['category_account'] == 'Other Income']
    other_expense1 = df_filtered1[df_filtered1['category_account'] == 'Other Expense']
    income_summary = revenue1['credit'].sum() - revenue1['debit'].sum() + expense1['credit'].sum() - expense1['debit'].sum()+ other_income1['credit'].sum() - other_income1['debit'].sum() + other_expense1['credit'].sum() - other_expense1['debit'].sum()-cogs1['debit'].sum()+cogs1['credit'].sum()

    return {'retained_earnings': retained_earnings, 'income_summary': income_summary, 'closest_year_end': closest_year_end}

def process_balance_sheet(fetch_data_func, end_date, table_name, company_name):
    # Fetch balance sheet data using the provided function
    df_bl = fetch_data_func(end_date, table_name)

    # Define categories and calculate effective balance for each
    categories = [
        "Fixed Asset", "Current Asset", "Revenue", "COGS", "Expense",
        "Other Income", "Other Expense", "Long-Term Liability", "Equity", "Current Liability"
    ]
    for category in categories:
        df_bl[category] = df_bl.apply(
            lambda row: (row['debit'] - row['credit']) if category in ["Fixed Asset", "Current Asset", "Expense", "Other Expense"] else (row['credit'] - row['debit']),
            axis=1
        )

    # Group by account and aggregate the amounts for each category
    result = {
        "company_name": company_name,
        "accounting_method": "Cash Basis",
        "end_date": end_date
    }
    for category in categories:
        grouped = df_bl[df_bl['category_account'] == category].groupby(['account']).agg(
            amount=pd.NamedAgg(column=category, aggfunc='sum')
        ).reset_index()
        result[category.lower().replace(" ", "_")] = grouped.apply(
            lambda row: {"category": category, "description": row['account'], "amount": row['amount']}, axis=1
        ).tolist()

    return result

def process_cash_flow_data(df, start_date, end_date):
    # Non-cash calculations
    revenue_nc = df[(df['category_account'] == 'Revenue') & (df['source_account'] != 'cash')]['credit'].sum() - \
                 df[(df['category_account'] == 'Revenue') & (df['source_account'] != 'cash')]['debit'].sum()
    expenses_nc = df[(df['category_account'] == 'Expense') & (df['source_account'] != 'cash')]['debit'].sum() - \
                  df[(df['category_account'] == 'Expense') & (df['source_account'] != 'cash')]['credit'].sum()
    other_income_nc = df[(df['category_account'] == 'Other Income') & (df['source_account'] != 'cash')]['credit'].sum() - \
                      df[(df['category_account'] == 'Other Income') & (df['source_account'] != 'cash')]['debit'].sum()
    other_expense_nc = df[(df['category_account'] == 'Other Expense') & (df['source_account'] != 'cash')]['debit'].sum() - \
                       df[(df['category_account'] == 'Other Expense') & (df['source_account'] != 'cash')]['credit'].sum()
    cogs_nc = df[(df['category_account'] == 'COGS') & (df['source_account'] != 'cash')]['debit'].sum() - \
              df[(df['category_account'] == 'COGS') & (df['source_account'] != 'cash')]['credit'].sum()

    # Cash-based calculations
    filtered_df = df[df['source_account'] == 'cash']
    fixed_asset = filtered_df[filtered_df['category_account'] == 'Fixed Asset']['debit'].sum() - \
                  filtered_df[filtered_df['category_account'] == 'Fixed Asset']['credit'].sum()
    equity = filtered_df[filtered_df['category_account'] == 'Equity']['credit'].sum() - \
             filtered_df[filtered_df['category_account'] == 'Equity']['debit'].sum()
    current_liability = filtered_df[filtered_df['category_account'] == 'Current Liability']['debit'].sum() - \
                        filtered_df[filtered_df['category_account'] == 'Current Liability']['credit'].sum()
    long_term_liability = filtered_df[filtered_df['category_account'] == 'Long-Term Liability']['debit'].sum() - \
                          filtered_df[filtered_df['category_account'] == 'Long-Term Liability']['credit'].sum()
    current_asset = filtered_df[filtered_df['category_account'] == 'Current Asset']['debit'].sum() - \
                    filtered_df[filtered_df['category_account'] == 'Current Asset']['credit'].sum()

    # Net Income calculation
    revenue = df[df['category_account'] == 'Revenue']['credit'].sum() - df[df['category_account'] == 'Revenue']['debit'].sum()
    expenses = df[df['category_account'] == 'Expense']['debit'].sum() - df[df['category_account'] == 'Expense']['credit'].sum()
    other_income = df[df['category_account'] == 'Other Income']['credit'].sum() - df[df['category_account'] == 'Other Income']['debit'].sum()
    other_expenses = df[df['category_account'] == 'Other Expense']['debit'].sum() - df[df['category_account'] == 'Other Expense']['credit'].sum()
    cogs = df[df['category_account'] == 'COGS']['debit'].sum() - df[df['category_account'] == 'COGS']['credit'].sum()
    net_income = revenue + other_income - expenses - other_expenses - cogs

    # Cash at start and end date calculations
    df_before_start = df[df['date'] == start_date]
    cash_credits_start = df_before_start[df_before_start['account'] == 'Cash']['credit'].sum()
    cash_debits_start = df_before_start[df_before_start['account'] == 'Cash']['debit'].sum()
    total_cash_start = cash_credits_start - cash_debits_start

    df_before_end = df[df['date'] == end_date]
    cash_credits_end = df_before_end[df_before_end['account'] == 'Cash']['credit'].sum()
    cash_debits_end = df_before_end[df_before_end['account'] == 'Cash']['debit'].sum()
    total_cash_end = cash_credits_end - cash_debits_end

    # Formatting the data
    formatted_data = [
        {"category": "Revenue", "description": "Revenue (non-cash)", "amount": revenue_nc},
        {"category": "Expense", "description": "Expenses (non-cash)", "amount": expenses_nc},
        {"category": "Other Income", "description": "Other Income (non-cash)", "amount": other_income_nc},
        {"category": "Other Expense", "description": "Other Expenses (non-cash)", "amount": other_expense_nc},
        {"category": "COGS", "description": "COGS (non-cash)", "amount": cogs_nc},
        {"category": "Fixed Asset", "description": "Fixed Asset", "amount": fixed_asset},
        {"category": "Equity", "description": "Equity", "amount": equity},
        {"category": "Current Liability", "description": "Current Liability", "amount": current_liability},
        {"category": "Long-Term Liability", "description": "Long-Term Liability", "amount": long_term_liability},
        {"category": "Current Asset", "description": "Current Asset", "amount": current_asset},
        {"category": "Revenue", "description": "Net Income", "amount": net_income},
        {"category": "Cash", "description": "Total Cash at Start Date", "amount": total_cash_start},
        {"category": "Cash", "description": "Total Cash at End Date", "amount": total_cash_end}
    ]

    return formatted_data

# Sample usage
# print(process_cash_flow_data(fetch_data("2019-01-01", "2023-12-31", "sample_company"), "2019-01-01", "2023-12-31"))
start_date = "2021-01-01"
end_date = "2022-12-31"
t_name = "sample_company"
df = fetch_data(start_date, end_date, t_name)
print(process_cash_flow_data(df, start_date, end_date))