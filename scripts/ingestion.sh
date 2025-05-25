#!/bin/bash
# scripts/ingestion/csv_to_hdfs.sh

# Create HDFS directories
hdfs dfs -mkdir -p /user/ecommerce/raw_data
hdfs dfs -mkdir -p /user/ecommerce/processed_data

# Upload CSV files
hdfs dfs -put /data/raw/csv/customers.csv /user/ecommerce/raw_data/
hdfs dfs -put /data/raw/csv/order_items.csv /user/ecommerce/raw_data/
hdfs dfs -put /data/raw/csv/products.csv /user/ecommerce/raw_data/
hdfs dfs -put /data/raw/csv/reviews.csv /user/ecommerce/raw_data/
hdfs dfs -put /data/raw/csv/sellers.csv /user/ecommerce/raw_data/
hdfs dfs -put /data/raw/csv/transactions.csv /user/ecommerce/raw_data/

echo "CSV files uploaded to HDFS successfully!"