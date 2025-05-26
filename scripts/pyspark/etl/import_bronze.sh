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

# Fungsi untuk mengimpor tabel
import_table() {
  local table_name=$1
  local target_dir="${BRONZE_BASE}/${table_name}"

  # Jika direktori sudah ada, hapus dulu
  if hdfs dfs -test -d ${target_dir}; then
    echo ">>> Menghapus existing ${target_dir}"
    hdfs dfs -rm -r ${target_dir}
  else
    echo ">>> ${target_dir} tidak ada, melanjutkan..."
  fi

  # Mengimpor tabel
  echo ">>> Mengimpor tabel ${table_name} ke ${target_dir}"
  sqoop import $COMMON_OPTS \
    --table ${table_name} \
    --target-dir ${target_dir} \
    --split-by id_pelanggan || { echo "Error importing ${table_name}"; exit 1; }
}

# Daftar tabel yang akan diimpor
tables=("customers" "products" "order_items" "reviews" "sellers" "transactions")

# Mengimpor semua tabel
for tbl in "${tables[@]}"; do
  import_table $tbl
done