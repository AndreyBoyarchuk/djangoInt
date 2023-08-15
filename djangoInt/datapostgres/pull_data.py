from djangoInt.datapostgres.postgres_connection import create_connection
import pandas as pd


engine = create_connection()

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

def process_financial_reports(df, company_name="Your Company Name", start_date="Start Date", end_date="End Date"):
    # Calculate the amount for income and expenses considering both debit and credit
    df['income_amount'] = df.apply(lambda row: row['credit'] if row['category_account'] == 'Revenue' else -row['debit'], axis=1)
    df['expense_amount'] = df.apply(lambda row: row['debit'] if row['category_account'] == 'Expense' else -row['credit'], axis=1)

    # Group by account and sum the amounts for income and expenses
    income_grouped = df[df['category_account'] == 'Revenue'].groupby(['account']).agg(
        amount=pd.NamedAgg(column='income_amount', aggfunc='sum')
    ).reset_index()

    expenses_grouped = df[df['category_account'] == 'Expense'].groupby(['account']).agg(
        amount=pd.NamedAgg(column='expense_amount', aggfunc='sum')
    ).reset_index()

    # Convert to the desired JSON structure
    result = {
        "company_name": company_name,
        "accounting_method": "Cash Basis",
        "start_date": start_date,
        "end_date": end_date,
        "income": income_grouped.apply(
            lambda row: {"category": "Operating Income", "description": row['account'], "amount": row['amount']}, axis=1
        ).tolist(),
        "expenses": expenses_grouped.apply(
            lambda row: {"category": "Operating Expenses", "description": row['account'], "amount": row['amount']}, axis=1
        ).tolist()
    }

    return result



