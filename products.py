import os
import csv
from dotenv import load_dotenv
from amazon_paapi import AmazonApi
from node_ids import get_node_ids

load_dotenv()

amazon_client = AmazonApi(
    key=os.environ.get("AMAZON_ACCESS_KEY"),
    secret=os.environ.get("AMAZON_SECRET_KEY"),
    country="IT",
    tag=os.environ.get("AMAZON_PARTNER_TAG"),
    throttling=2  
)

def extract_amazon_product_fields(item):
    if not isinstance(item, dict):
        return {}
    offers = item.get("offers") or {}
    listings = offers.get("listings") or []
    listing = listings[0] if listings else {}
    categories = [
        node.get('display_name')
        for node in (item.get("browse_node_info") or {}).get("browse_nodes", [])
    ]
    return {
        "product_id": item.get("asin"),
        "image_url": ((item.get("images") or {}).get("primary") or {}).get("large", {}).get("url"),
        "price": (listing.get("price") or {}).get("amount"),
        "currency": (listing.get("price") or {}).get("currency"),
        "availability": ((listing.get("availability") or {}).get("max_order_quantity") or 0),
        "categories": categories[0] if categories else None,
        "product_link": item.get("detail_page_url"),
        "description": (item.get("item_info") or {}).get("title", {}).get("display_value", []),
    }

def get_products_and_write(node_ids, filename="products.csv"):
    first_row = True
    with open(filename, mode="w", encoding="utf-8", newline='') as f:
        writer = None
        for node_id in node_ids:
            try:
                # Increase 'item_count' to fetch multiple products in one call
                results = amazon_client.search_items(
                    browse_node_id=node_id,
                    item_count=10,
                    item_page=1
                )
                for item in results.items:
                    item_dict = item.to_dict()
                    product_data = extract_amazon_product_fields(item_dict)
                    # Initialize CSV writer with fieldnames once
                    if first_row:
                        writer = csv.DictWriter(f, fieldnames=product_data.keys())
                        writer.writeheader()
                        first_row = False
                    writer.writerow(product_data)
            except Exception as e:
                None
                # print(f"Error fetching products for node {node_id}: {e}")

def main():
    file_path = "data/it.eu_browse_tree_mappings._TTH_.xls"
    node_ids = get_node_ids(file_path)
    node_ids = node_ids
    print(f"Found {len(node_ids)} child categories. Fetching products...")
    get_products_and_write(node_ids)
    print("All the nodes have been explored and saved the products in CSV file.")