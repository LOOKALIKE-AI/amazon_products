from amazon_paapi import AmazonApi
import os
import csv
from dotenv import load_dotenv

load_dotenv()

# Initialize Amazon API Client
amazon_client = AmazonApi(
    key=os.environ.get("AMAZON_ACCESS_KEY"),
    secret=os.environ.get("AMAZON_SECRET_KEY"),
    country="IT",
    tag=os.environ.get("AMAZON_PARTNER_TAG"),
    throttling=5
)

# Get the exact details from the results
def extract_amazon_product_fields(item):
    if not isinstance(item, dict):
        return {}

    offers = item.get("offers") or {}
    listings = offers.get("listings") or []
    listing = listings[0] if listings else {}

    categories = [
        {
            'display_name': node.get('display_name')
        }
        for node in (item.get("browse_node_info") or {}).get("browse_nodes", [])
    ]

    return {
        "product_id": item.get("asin"),
        "image_url": ((item.get("images") or {}).get("primary") or {}).get("large", {}).get("url"),
        "price": (listing.get("price") or {}).get("amount"),
        "currency": (listing.get("price") or {}).get("currency"),
        "availability": ((listing.get("availability") or {}).get("max_order_quantity") or 0),
        "categories": categories[0]["display_name"],
        "product_link": item.get("detail_page_url"),
        "description": (item.get("item_info") or {}).get("features", {}).get("display_values", []),
    }



# Get child browse nodes of a main category (e.g., Beauty)
def get_child_node_ids(main_node_id="6198083031"):
    browser_nodes = amazon_client.get_browse_nodes(browse_node_ids=[main_node_id])
    child_node_ids = []

    for node in browser_nodes:
        for child in node.children:
            child_node_ids.append(child.id)
    
    return child_node_ids

# Search products for each child node
def get_products_from_children(child_node_ids, search_index="Beauty"):
    all_products = []

    for node_id in child_node_ids:
        try:
            for page in range(1, 2):  
                results = amazon_client.search_items(
                    browse_node_id=node_id,
                    search_index=search_index,
                    item_count=1,
                    item_page=page
                )

                for item in results.items:
                    item_dict = item.to_dict()
                    if not isinstance(item_dict, dict):
                        print(f"Skipping item: not a valid dict -> {item_dict}")
                        continue
                    product_data = extract_amazon_product_fields(item_dict)
                    all_products.append(product_data)

        except Exception as e:
            print(f"Error fetching products for node {node_id}: {e}")

    return all_products

# Save all product data to CSV
def save_products_to_csv(products, filename="beauty_products.csv"):
    if not products:
        print("No products to save.")
        return

    # Flatten 'description' fields
    for product in products:
        if not isinstance(product, dict):
            print(f"⚠️ Skipping invalid product entry: {product}")
            continue
        if isinstance(product.get("description"), list):
            product["description"] = "\n".join(product["description"])

    fieldnames = products[0].keys()

    try:
        with open(filename, mode="w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        print(f" Saved {len(products)} products to {filename}")
        
    except Exception as e:
        print(f" Error writing CSV: {e}")

# Main execution
def main():
    print("Getting child nodes for Beauty...")
    children = get_child_node_ids("6198083031")  # Beauty

    print(f"Found {len(children)} child categories. Fetching products...")
    products = get_products_from_children(children)

    print("Saving products to CSV...")
    save_products_to_csv(products)
