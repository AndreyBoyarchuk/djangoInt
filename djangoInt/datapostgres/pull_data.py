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
