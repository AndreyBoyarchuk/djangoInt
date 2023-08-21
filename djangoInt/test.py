from djangoInt.datapostgres.postgres_connection import create_connection
import pandas as pd


engine = create_connection()
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

    # ... rest of the code remains the same ...


    # Calculate net income (total revenue - total expenses) for the filtered data
    revenue = df_filtered[df_filtered['category_account'] == 'Revenue']
    expense = df_filtered[df_filtered['category_account'] == 'Expense']
    retained_earnings = revenue['credit'].sum() - revenue['debit'].sum() + expense['credit'].sum() - expense['debit'].sum()

    revenue1 = df_filtered1[df_filtered1['category_account'] == 'Revenue']
    expense1 = df_filtered1[df_filtered1['category_account'] == 'Expense']
    income_summary = revenue1['credit'].sum() - revenue1['debit'].sum() + expense1['credit'].sum() - expense1['debit'].sum()

    return {'retained_earnings': retained_earnings, 'income_summary': income_summary, 'closest_year_end': closest_year_end}







print(calculate_summary_or_retained_earnings(fetch_bl_equity('2023-10-30', 'sample_company'), '2022-10-30'))



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
