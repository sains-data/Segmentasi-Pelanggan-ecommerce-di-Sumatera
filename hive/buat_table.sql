-- scripts/ingestion/create_hive_tables.sql
CREATE DATABASE IF NOT EXISTS ecommerce_sumatera;
USE ecommerce_sumatera;

-- Customers table
CREATE EXTERNAL TABLE IF NOT EXISTS customers (
    id_pelanggan STRING,
    kota_kabupaten_pelanggan STRING,
    provinsi_pelanggan STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/ecommerce/raw_data/customers/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Order items table
CREATE EXTERNAL TABLE IF NOT EXISTS order_items (
    id_order STRING,
    id_produk STRING,
    harga DOUBLE,
    jumlah INT,
    total_item DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/ecommerce/raw_data/order_items/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Products table
CREATE EXTERNAL TABLE IF NOT EXISTS products (
    id_produk STRING,
    id_seller STRING,
    kategori_produk STRING,
    harga DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/ecommerce/raw_data/products/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Reviews table
CREATE EXTERNAL TABLE IF NOT EXISTS reviews (
    id_pelanggan STRING,
    id_produk STRING,
    nilai_rating_produk DOUBLE,
    tanggal_review STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/ecommerce/raw_data/reviews/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Sellers table
CREATE EXTERNAL TABLE IF NOT EXISTS sellers (
    id_seller STRING,
    kota_kabupaten_seller STRING,
    provinsi_seller STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/ecommerce/raw_data/sellers/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Transactions table
CREATE EXTERNAL TABLE IF NOT EXISTS transactions (
    id_order STRING,
    id_pelanggan STRING,
    metode_pembayaran STRING,
    banyak_cicilan INT,
    total_pembayaran DOUBLE,
    status_order STRING,
    timestamp_pembelian STRING,
    timestamp_persetujuan_toko STRING,
    timestamp_pengiriman_ke_pelanggan STRING,
    estimasi_sampai STRING
)

CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_analytics.customer_segments_enhanced
STORED AS PARQUET
LOCATION 'hdfs://namenode:9000/data/gold/customer_segments_enhanced';

ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/ecommerce/raw_data/transactions/'
TBLPROPERTIES ("skip.header.line.count"="1");