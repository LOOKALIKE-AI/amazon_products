# Amazon Product Extraction for Italy (Beauty Category)

## Overview

This project extracts product data from Amazon Italy (amazon.it), focusing on the **Beauty** category and its child browse nodes. It uses the **Amazon Product Advertising API (PAAPI)** via the `amazon_paapi` Python package to retrieve product details and stores the results in a CSV file.

The extraction process runs automatically on a schedule using **GitHub Actions**.


## Features

- Retrieves browse node children for a main category (default: Beauty, node ID `6198083031`).
- Searches Amazon products within each child browse node.
- Extracts detailed product info: ASIN, price, currency, availability, categories, description, image URL, and product link.
- Saves all products into a CSV (`beauty_products.csv`).
- Automates periodic runs via GitHub Actions.
- Uses environment variables to protect sensitive Amazon credentials.

