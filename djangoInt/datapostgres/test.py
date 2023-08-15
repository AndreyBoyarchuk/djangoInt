from pull_data import fetch_data, transactions_history, fetch_summary , process_financial_reports


# Example usage
start_date = '07/01/2023'
end_date = '07/05/2023'
t_name = 'sample_company'
df = fetch_data(start_date, end_date, t_name)
result = process_financial_reports(df, start_date=start_date, end_date=end_date)
print(result)

import json

# Assuming 'result' is the dictionary returned by the process_profit_and_loss function
json_output = json.dumps(result, indent=4)

# Print the JSON string
print(json_output)

# If you want to write the JSON string to a file
with open('profit_and_loss.json', 'w') as file:
    file.write(json_output)
column_names = df.columns.tolist()

print(column_names)