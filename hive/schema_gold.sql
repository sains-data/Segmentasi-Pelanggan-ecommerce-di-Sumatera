CREATE TABLE IF NOT EXISTS gold_segmentasi_pelanggan (
    id_pelanggan STRING,
    segment INT,
    avg_harga DOUBLE,
    total_transaksi INT,
    last_pembelian TIMESTAMP,
    provinsi_pelanggan STRING
)
STORED AS PARQUET
LOCATION '/data/gold/segmentasi_pelanggan';
