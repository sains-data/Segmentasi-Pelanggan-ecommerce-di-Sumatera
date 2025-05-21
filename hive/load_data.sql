-- Load data parquet dari HDFS ke tabel Hive external
MSCK REPAIR TABLE bronze_pelanggan;
MSCK REPAIR TABLE gold_segmentasi_pelanggan;
