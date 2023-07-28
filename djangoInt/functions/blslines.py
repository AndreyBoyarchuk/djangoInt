import json
import matplotlib.pyplot as plt
import os

def load_json_file(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

def plot_balance_sheet(data):
    quarters = list(data['2023'].keys())
    assets = [data['2023'][quarter]['Assets'] for quarter in quarters]
    liabilities = [-data['2023'][quarter]['Liabilities'] for quarter in quarters]
    equity = [-data['2023'][quarter]['Equity'] for quarter in quarters]
    current_assets = [data['2023'][quarter]['CurrentAssets'] for quarter in quarters]

    plt.figure(figsize=(10, 6))

    bar1 = plt.bar(quarters, assets, label='Assets')
    bar2 = plt.bar(quarters, liabilities, label='Liabilities')
    bar3 = plt.bar(quarters, equity, label='Equity')
    bar4 = plt.bar(quarters, current_assets, label='Current Assets')

    plt.xlabel('Quarters')
    plt.ylabel('Values')
    plt.title('Balance Sheet 2023')
    plt.legend()

    # function to add labels to the bars
    def add_labels(bars):
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom') # va='bottom' to make the text appear just above the bar

    add_labels(bar1)
    add_labels(bar2)
    add_labels(bar3)
    add_labels(bar4)

    image_path = os.path.join('static', 'images', 'balance_sheet.png')
    if os.path.exists(image_path):
        os.remove(image_path)
    plt.savefig(os.path.join('static', 'images', 'balance_sheet.png'))

    plt.close()



data = load_json_file(os.path.join('djangoInt', 'jsons', 'ratios.json'))

plot_balance_sheet(data)
