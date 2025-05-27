#!/bin/bash
# Pastikan HDFS sudah dijalankan: start-dfs.sh
hdfs dfs -mkdir -p /data/bronze/order_items
hdfs dfs -put -f /mnt/c/Segmentasi-Pelanggan-ecommerce-di-Sumatera/data/order_items.csv /data/bronze/order_items/