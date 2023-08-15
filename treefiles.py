import os

def create_folder_tree(root_directory, output_file, skip_directories):
    with open(output_file, 'w') as file:
        write_folder_tree(root_directory, file, '', skip_directories)

def write_folder_tree(directory, file, indent='', skip_directories=[]):
    file.write(f"{indent}{os.path.basename(directory)}\n")
    indent += '|   '
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and item not in skip_directories:  # Skip directories from the list
            write_folder_tree(item_path, file, indent, skip_directories)
        elif os.path.isfile(item_path):
            file.write(f"{indent}|-- {item}\n")

root_directory = os.getcwd()  # Use the current working directory as the root directory
output_file = 'structure.txt'
skip_directories = ['venv', 'node_modules', '__pycache__','documents','idea','.git','.idea','staticfiles']  # List directories to skip here
create_folder_tree(root_directory, output_file, skip_directories)
print(f"Folder structure saved in {output_file} successfully!")
