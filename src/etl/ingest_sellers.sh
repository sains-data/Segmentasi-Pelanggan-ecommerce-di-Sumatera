#!/bin/bash
# Pastikan HDFS sudah dijalankan: start-dfs.sh
hdfs dfs -mkdir -p /data/bronze/sellers
hdfs dfs -put -f /mnt/c/Segmentasi-Pelanggan-ecommerce-di-Sumatera/data/sellers.csv /data/bronze/sellers/