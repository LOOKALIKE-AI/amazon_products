import pandas as pd


def get_node_ids(file_path):

    data = pd.read_excel(file_path, sheet_name=1)
    unwanted_node_roots = ['it-automotive', 'it-baby-products', 'it-computers', 'it-electronics', 'it-garden', 'it-grocery', 'it-handmade', 'it-health', 'it-industrial', 'it-lighting', 'it-luggage', 'it-musical-instruments', 'it-office-products', 'it-sporting-goods', 'it-tools', 'it-toys']

    filtered_data = data[~data['Node root'].isin(unwanted_node_roots)]
    node_ids = filtered_data['Node ID'].astype(str).tolist()
    return node_ids

file_path = "./data/it.eu_browse_tree_mappings._TTH_.xls"
# node_ids = get_node_ids(file_path)
# print(node_ids)


