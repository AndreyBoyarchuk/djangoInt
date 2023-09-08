from pull_data import fetch_data, fetch_summary, transactions_history, process_profit_and_loss, fetch_bl_data
import json
from djangoInt.datapostgres.postgres_connection import create_connection

engine = create_connection()
import pandas as pd


def process_cash_flow_data(df, df1, df2, start_date, end_date):
    nocash_df = df[df['source_account'] != 'cash']

    nocash_df['amount'] = df.apply(
        lambda row: (row['debit'] - row['credit']) if row['category_account'] in ["Fixed Asset", "Current Asset", "Revenue", "COGS", "Expense"]  # only for expense accounts
        else (row['credit'] - row['debit']),  # if category account is Other Income or Revenue
        axis=1
    )

    grouped = nocash_df.groupby(['category_account', 'account']).sum().reset_index()
    print(grouped)
    revenue_nc = df[(df['category_account'] == 'Revenue') & (df['source_account'] != 'cash')]['credit'].sum() - \
                 df[(df['category_account'] == 'Revenue') & (df['source_account'] != 'cash')]['debit'].sum()
    expenses_nc = df[(df['category_account'] == 'Expense') & (df['source_account'] != 'cash')]['debit'].sum() - \
                  df[(df['category_account'] == 'Exp`ense') & (df['source_account'] != 'cash')]['credit'].sum()
    other_income_nc = df[(df['category_account'] == 'Other Income') & (df['source_account'] != 'cash')][
                          'credit'].sum() - \
                      df[(df['category_account'] == 'Other Income') & (df['source_account'] != 'cash')]['debit'].sum()
    other_expense_nc = df[(df['category_account'] == 'Other Expense') & (df['source_account'] != 'cash')][
                           'debit'].sum() - \
                       df[(df['category_account'] == 'Other Expense') & (df['source_account'] != 'cash')][
                           'credit'].sum()
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
    revenue = df[df['category_account'] == 'Revenue']['credit'].sum() - df[df['category_account'] == 'Revenue'][
        'debit'].sum()
    expenses = df[df['category_account'] == 'Expense']['debit'].sum() - df[df['category_account'] == 'Expense'][
        'credit'].sum()
    other_income = df[df['category_account'] == 'Other Income']['credit'].sum() - \
                   df[df['category_account'] == 'Other Income']['debit'].sum()
    other_expenses = df[df['category_account'] == 'Other Expense']['debit'].sum() - \
                     df[df['category_account'] == 'Other Expense']['credit'].sum()
    cogs = df[df['category_account'] == 'COGS']['debit'].sum() - df[df['category_account'] == 'COGS']['credit'].sum()
    net_income = revenue + other_income - expenses - other_expenses - cogs

    # Cash at start and end date calculations
    df_before_start = df1[df1['account'] == 'cash']
    cash_credits_start = df_before_start[df_before_start['account'] == 'cash']['credit'].sum()
    cash_debits_start = df_before_start[df_before_start['account'] == 'cash']['debit'].sum()
    total_cash_start = cash_debits_start - cash_credits_start
    df_before_end = df2[df2['account'] == 'cash']
    cash_credits_end = df_before_end[df_before_end['account'] == 'cash']['credit'].sum()
    cash_debits_end = df_before_end[df_before_end['account'] == 'cash']['debit'].sum()
    total_cash_end = cash_debits_end - cash_credits_end

    # Formatting the data
    formatted_data = [
        {"category": "Revenue", "account": "account", "description": "revenue_none_cash", "amount": revenue_nc},
        {"category": "Expense", "account": "account", "description": "expenses_none_cash", "amount": expenses_nc},
        {"category": "Other Income", "account": "account", "description": "other_income_none_cash",
         "amount": other_income_nc},
        {"category": "Other Expense", "account": "account", "description": "other-expenses_none_cash",
         "amount": other_expense_nc},
        {"category": "COGS", "account": "account", "description": "cogs_none_cash", "amount": cogs_nc},
        {"category": "Fixed Asset", "account": "account", "description": "fixed_asset", "amount": fixed_asset},
        {"category": "Equity", "account": "account", "description": "Equity", "amount": equity},
        {"category": "Current Liability", "account": "account", "description": "Current Liability",
         "amount": current_liability},
        {"category": "Long-Term Liability", "account": "account", "description": "Long-Term Liability",
         "amount": long_term_liability},
        {"category": "Current Asset", "account": "account", "description": "Current Asset", "amount": current_asset},
        {"category": "Revenue", "account": "account", "description": "Net Income", "amount": net_income},
        {"category": "Cash", "account": "account", "description": "Total Cash at Start Date",
         "amount": total_cash_start},
        {"category": "Cash", "account": "account", "description": "Total Cash at End Date", "amount": total_cash_end}
    ]
    with open('data.json', 'w') as file:
        json.dump(formatted_data, file, indent=4)

    return formatted_data


start_date = "2021-01-01"
end_date = "2022-12-31"
t_name = "sample_company"
df = fetch_data(start_date, end_date, t_name)
df1 = fetch_bl_data(start_date, t_name)
df2 = fetch_bl_data(end_date, t_name)
