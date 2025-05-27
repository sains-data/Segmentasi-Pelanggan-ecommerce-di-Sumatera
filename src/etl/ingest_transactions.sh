#!/bin/bash
# Pastikan HDFS sudah dijalankan: start-dfs.sh
hdfs dfs -mkdir -p /data/bronze/transactions
hdfs dfs -put -f /mnt/c/Segmentasi-Pelanggan-ecommerce-di-Sumatera/data/transactions.csv /data/bronze/transactions/