from djangoInt.datapostgres.postgres_connection import create_connection
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
        lambda row: (row['debit'] - row['credit']) if row['category_account'] in ["Expense", "COGS", "Other Expense"] #only for expense accounts
        else (row['credit'] - row['debit']), # if category account is Other Income or Revenue
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
    query = f"""SELECT account, category_account, SUM(debit) AS debit, SUM(credit) AS credit FROM {table_name} WHERE date < '{end_date}' GROUP BY account, category_account"""
    df_bl = pd.read_sql_query(query, engine)
    return df_bl

def fetch_bl_equity(end_date, t_name): #this funciton bring transactions ungrouped which allows to filter by date
    query = f"""SELECT * FROM fetch_bl_data('{end_date}', '{t_name}')"""
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

def process_balance_sheet(fetch_bl_data, end_date, table_name, company_name):
    # Fetch balance sheet data using the provided function
    df_bl = fetch_bl_data(end_date, table_name)

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

def process_cash_flow_data(df, df1, df2, t_name, start_date, end_date):
    # _________________________________________________
    nocash_df = df[df['source_account'] != 'cash']
    # nonecash transactions filter
    grouped = nocash_df.groupby(['category_account', 'account','source_account']).agg({
        'debit': 'sum',
        'credit': 'sum'
    }).reset_index()
    # _________________________________________________
    cash_df = df[df['source_account'] == 'cash']
    # cash transactions filtered
    grouped2 = cash_df.groupby(['category_account', 'account','source_account']).agg({
        'debit': 'sum',
        'credit': 'sum'
    }).reset_index()
    # Cash Balances
    # Cash starting balance
    df_before_start = df1[df1['account'] == 'cash']
    cash_credits_start = df_before_start[df_before_start['account'] == 'cash']['credit'].sum()
    cash_debits_start = df_before_start[df_before_start['account'] == 'cash']['debit'].sum()
    # Cash ending balance
    df_before_end = df2[df2['account'] == 'cash']
    cash_credits_end = df_before_end[df_before_end['account'] == 'cash']['credit'].sum()
    cash_debits_end = df_before_end[df_before_end['account'] == 'cash']['debit'].sum()

    cash_balances_df = pd.DataFrame({
        'category_account': ['Cash Balance', 'Cash Balance'],
        'account': ['Cash Start', 'Cash End'],
        'debit': [cash_debits_start, cash_debits_end],
        'credit': [cash_credits_start, cash_credits_end],
        'indicator': ['balance', 'balance'],
        'source_account': ['cash', 'cash']
    })
    grouped['indicator'] = 'none_cash'
    grouped2['indicator'] = 'cash'

    # grouped['account'] = grouped['account'].apply(lambda x: f"{x}_none_cash")
    # grouped2['account'] = grouped2['account'].apply(lambda x: f"{x}_cash")
    combined_df = pd.concat([grouped, grouped2, cash_balances_df])
    combined_df = combined_df.reset_index(drop=True)
    return combined_df



