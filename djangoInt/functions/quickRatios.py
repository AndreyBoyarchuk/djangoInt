import json
import matplotlib.pyplot as plt
import os

def load_json_file(file_path):
    with open(file_path) as file:
        data = json.load(file)
    return data

def plot_quick_ratio(data):
    quarters = list(data['2023'].keys())
    quick_ratio = [(data['2023'][quarter]['CurrentAssets'] - data['2023'][quarter]['Inventory']) / data['2023'][quarter]['CurrentLiabilities'] for quarter in quarters]

    plt.figure(figsize=(10, 6))

    plt.bar(quarters, quick_ratio, label='Quick Ratio')

    plt.xlabel('Quarters')
    plt.ylabel('Ratio')
    plt.title('Quick Ratio 2023')
    plt.legend()

    image_path = os.path.join('static', 'images', 'quick_ratio.png')
    if os.path.exists(image_path):
        os.remove(image_path)

    plt.savefig(image_path)

    plt.close()

data = load_json_file(os.path.join('djangoInt', 'jsons', 'ratios.json'))
plot_quick_ratio(data)
