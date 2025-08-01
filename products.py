import os
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
import pandas as pd
import csv
import time
import requests

# Load .env environment variables
load_dotenv()

class GetProducts:
    def __init__(self):
        # Store the Amazon client in the instance
        self.amazon_client = AmazonApi(
            key=os.environ.get("AMAZON_ACCESS_KEY"),
            secret=os.environ.get("AMAZON_SECRET_KEY"),
            country="IT",
            tag=os.environ.get("AMAZON_PARTNER_TAG"),
            throttling=1
        )

    def extract_required_fields(self, item: dict) -> dict:
        """Extract relevant fields from an Amazon API item."""
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
            "description": (item.get("item_info") or {}).get("title", {}).get("display_value", ""),
        }

    @staticmethod
    def get_node_ids(file_path: str) -> list:
        """Read node IDs from Excel and filter unwanted roots."""
        data = pd.read_excel(file_path, sheet_name=1, usecols=['Node root', 'Node ID'])
        unwanted_node_roots = [
            'it-automotive', 'it-computers', 'it-electronics', 'it-grocery',
            'it-industrial', 'it-lighting', 'it-musical-instruments', 'it-tools', 'it-toys'
        ]
        filtered_data = data[~data['Node root'].isin(unwanted_node_roots)]
        return filtered_data['Node ID'].astype(str).tolist()

    def search_items(self, node_ids=None, csv_name="beauty_products.csv"):
        """Search items by node IDs and/or searchindex, save to CSV, and count products saved."""
        writer = None
        product_count = 0

        with open(csv_name, mode='w', encoding='utf-8', newline='') as f:
            for node_id in node_ids or []:
                try:
                    results_node = self.amazon_client.search_items(
                        browse_node_id=node_id,
                        item_count=10,
                        item_page=1
                    )

                    for item in results_node.items:
                        product_data = self.extract_required_fields(item.to_dict())
                        if product_data:
                            if writer is None:
                                writer = csv.DictWriter(f, fieldnames=product_data.keys())
                                writer.writeheader()
                            writer.writerow(product_data)
                            product_count += 1

                    time.sleep(2.3)  

                except Exception as e:
                    if any(keyword in str(e).lower() for keyword in ["requests limit reached", "throttling", "rate limit"]):
                        print(f"[!] Rate limit hit on Node ID: {node_id}. Stopping script.")
                        break


        return product_count

def main():
    gp = GetProducts()
    file_path = "./data/it.eu_browse_tree_mappings._TTH_.xls"

    # Get node IDs and searchindex
    node_ids = gp.get_node_ids(file_path)
    node_ids = node_ids[:8500]

    # Run search
    total_saved = gp.search_items(node_ids=node_ids)
    print(f"[INFO] Total products saved so far: {total_saved}")
