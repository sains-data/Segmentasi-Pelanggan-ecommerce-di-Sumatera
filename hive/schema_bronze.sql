CREATE EXTERNAL TABLE IF NOT EXISTS bronze_pelanggan (
    id_pelanggan STRING,
    provinsi_pelanggan STRING,
    harga DOUBLE,
    total_pembayaran DOUBLE,
    kategori_produk STRING,
    status_order STRING,
    timestamp_pembelian TIMESTAMP,
    -- kolom lain sesuai dataset
)
STORED AS PARQUET
LOCATION '/data/bronze/pelanggan';