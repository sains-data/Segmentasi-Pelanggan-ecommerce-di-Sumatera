#!/bin/bash
# Pastikan HDFS sudah dijalankan: start-dfs.sh
hdfs dfs -mkdir -p /data/bronze/products
hdfs dfs -put -f /mnt/c/Segmentasi-Pelanggan-ecommerce-di-Sumatera/data/products.csv /data/bronze/products/