#!/bin/bash

# import_bronze.sh
# Import semua tabel ke HDFS/Parquet (bronze layer)
# MySQL connection
MYSQL_CONN="jdbc:mysql://mysql-server:3306/ecommerce"
MYSQL_USER="root"
MYSQL_PASS="root"

# Lokasi bronze di HDFS
BRONZE_BASE="/data/bronze"

# Common options
COMMON_OPTS="--connect ${MYSQL_CONN} \
  --username ${MYSQL_USER} --password ${MYSQL_PASS} \
  --as-parquetfile \
  --compression-codec snappy \
  --null-string '\\N' --null-non-string '\\N' \
  -m 4"

for tbl in customers products order_items reviews sellers transactions; do
  TARGET=${BRONZE_BASE}/${tbl}

  # 1) Jika direktori sudah ada, hapus dulu
  if hdfs dfs -test -d ${TARGET}; then
    echo ">>> Menghapus existing ${TARGET}"
    hdfs dfs -rm -r ${TARGET}
  fi

# 1) customers
sqoop import $COMMON_OPTS \
  --table customers \
  --target-dir ${BRONZE_BASE}/customers \
  --split-by id_pelanggan

# 2) products
sqoop import $COMMON_OPTS \
  --table products \
  --target-dir ${BRONZE_BASE}/products \
  --split-by id_produk

# 3) order_items
sqoop import $COMMON_OPTS \
  --table order_items \
  --target-dir ${BRONZE_BASE}/order_items \
  --split-by id_order

# 4) reviews
sqoop import $COMMON_OPTS \
  --table reviews \
  --target-dir ${BRONZE_BASE}/reviews \
  --split-by id_pelanggan

# 5) sellers
sqoop import $COMMON_OPTS \
  --table sellers \
  --target-dir ${BRONZE_BASE}/sellers \
  --split-by id_seller

# 6) transactions
sqoop import $COMMON_OPTS \
  --table transactions \
  --target-dir ${BRONZE_BASE}/transactions \
  --split-by id_order