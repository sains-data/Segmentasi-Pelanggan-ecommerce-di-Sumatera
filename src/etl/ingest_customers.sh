#!/bin/bash
# Pastikan HDFS sudah dijalankan: start-dfs.sh
hdfs dfs -mkdir -p /data/bronze/customers
hdfs dfs -put -f /mnt/c/Segmentasi-Pelanggan-ecommerce-di-Sumatera/data/customers.csv /data/bronze/customers/