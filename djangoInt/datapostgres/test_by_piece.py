from pull_data import fetch_data, fetch_summary, transactions_history, process_profit_and_loss, fetch_bl_data
import json
from djangoInt.datapostgres.postgres_connection import create_connection

engine = create_connection()
import pandas as pd

start_date = "2021-01-01"
end_date = "2023-12-31"
t_name = "sample_company"
df = fetch_data(start_date, end_date, t_name)
df1 = fetch_bl_data(start_date, t_name)
df2 = fetch_bl_data(end_date, t_name)

unique_df = df[['category_account', 'account']].drop_duplicates().reset_index(drop=True)
df=df[df['account'] != 'cash']
df=df.reset_index(drop=True)
# Initialize an empty 'source_category' column in df
df['source_category'] = ''

# Loop through each row in unique_df to get each unique 'account'
for idx, row in unique_df.iterrows():
    account = row['account']
    category_account = row['category_account']
    # Update 'source_category' in df where 'account' matches 'source_account'
    df.loc[df['source_account'] == account, 'source_category'] = category_account
# For any remaining rows in df where 'source_category' is still empty, set it to 'Other'
df.loc[df['source_category'] == '', 'source_category'] = 'Other'

#_________________________________________________
nocash_df = df[df['source_account'] != 'cash']
# nonecash transactions filter
none_cash_df = nocash_df.groupby(['category_account', 'account', 'source_account', 'source_category']).agg({
    'debit': 'sum',
    'credit': 'sum'
}).reset_index()
#_________________________________________________
cash_set = df[df['source_account'] == 'cash']
# cash transactions filtered
cash_df = cash_set.groupby(['category_account', 'account', 'source_account', 'source_category']).agg({
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
    'source_account': ['balance', 'cash'],
    'indicator': ['balance', 'balance'],
    'source_category': ['balance', 'balance'],
    'cash_flow_direct': ['start_balance', 'end_balance'],
    'cash_flow_indirect': ['start_balance', 'end_balance'],
})
none_cash_df['indicator'] = 'none_cash'
cash_df['indicator'] = 'cash'

#grouped['account'] = grouped['account'].apply(lambda x: f"{x}_none_cash")
#grouped2['account'] = grouped2['account'].apply(lambda x: f"{x}_cash")
combined_df = pd.concat([none_cash_df, cash_df, cash_balances_df])
combined_df = combined_df.reset_index(drop=True)
# Convert DataFrame to JSON

pd.set_option('display.max_columns', None)  # None means unlimited
pd.set_option('display.width', 2000)  # Adjust as needed
#combined_df['cash_flow_direct'] = ''
#combined_df['cash_flow_indirect'] = ''

print(combined_df.columns)

"""
json_output = {}

# Get unique 'category_account' values
unique_categories = combined_df['category_account'].unique()

# Loop through each unique 'category_account' to create JSON objects
for category in unique_categories:
    sub_df = combined_df[combined_df['category_account'] == category]
    json_object = sub_df.to_dict(orient='records')
    json_output[category] = json_object

# Convert the entire dictionary to a JSON-formatted string
json_str = json.dumps(json_output, indent=4)

# Print or save the JSON-formatted string
print(json_str)
combined_df.to_csv('combined_df.csv', index=False) """  #save to csv and json

operating_activities_set = ['COGS', 'Revenue', 'Expense', 'Other Income', 'Other Expense']
financing_categories = ['Equity', 'Long-Term Liability', 'Current Liability']
investing_categories = ['Fixed Asset', 'Current Asset']
combined_df.loc[(combined_df['category_account'].isin(operating_activities_set)), 'cash_flow_indirect'] = 'Operating Activities'
combined_df.loc[(combined_df['category_account'].isin(financing_categories)), 'cash_flow_indirect'] = 'Financing Activities'
combined_df.loc[(combined_df['category_account'].isin(investing_categories)), 'cash_flow_indirect'] = 'Investing Activities'

combined_df.loc[(combined_df['source_category'].isin(operating_activities_set)) & (combined_df['indicator'] == 'none_cash'), 'cash_flow_indirect'] = 'Operating Activities'
combined_df.loc[(combined_df['source_category'].isin(financing_categories)) & (combined_df['indicator'] == 'none_cash'), 'cash_flow_indirect'] = 'Financing Activities'
combined_df.loc[(combined_df['source_category'].isin(investing_categories)) & (combined_df['indicator'] == 'none_cash'), 'cash_flow_indirect'] = 'Investing Activities'
combined_df.loc[(combined_df['category_account'].isin(operating_activities_set)) & (combined_df['indicator'] == 'cash'), 'cash_flow_direct'] = 'Operating Activities'
combined_df.loc[(combined_df['category_account'].isin(financing_categories)) & (combined_df['indicator'] == 'cash'), 'cash_flow_direct'] = 'Financing Activities'
combined_df.loc[(combined_df['category_account'].isin(investing_categories)) & (combined_df['indicator'] == 'cash'), 'cash_flow_direct'] = 'Investing Activities'


pl_filtered_df = combined_df[combined_df['category_account'].isin(operating_activities_set)]
# Reset the index for the filtered DataFrame and store it
pl_filtered_index = pl_filtered_df.index
# Set 'cash_flow_indirect' to 'Net Income' only for rows that are in pl_filtered_df
combined_df.loc[pl_filtered_index, 'cash_flow_indirect'] = 'net_income'

print(combined_df.head(50))
# Reset the index for the new DataFrame
combined_df.to_csv('combined_df.csv')