from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, to_date, when, lit, regexp_replace, trim
import os

# Inisialisasi Spark Session
spark = SparkSession.builder \
    .appName("Bronze to Silver ETL") \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://hive-server:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Path HDFS
bronze_path = "hdfs://namenode:9000/data/bronze"
silver_path = "hdfs://namenode:9000/data/silver"

# Fungsi untuk membaca data dari bronze layer
def read_bronze_data(table_name):
    print(f"Reading {table_name} data from bronze layer...")
    return spark.read.option("header", "true").option("inferSchema", "true").csv(f"{bronze_path}/{table_name}")

# Fungsi untuk membersihkan data pelanggan
def clean_customers(df):
    print("Cleaning customers data...")
    return df.withColumn("kode_pos_pelanggan", 
                       when(col("kode_pos_pelanggan").isNull(), lit("00000"))
                       .otherwise(col("kode_pos_pelanggan"))) \
            .dropDuplicates(["id_pelanggan"]) \
            .withColumn("kota_kabupaten_pelanggan", trim(col("kota_kabupaten_pelanggan"))) \
            .withColumn("provinsi_pelanggan", trim(col("provinsi_pelanggan")))

# Fungsi untuk membersihkan data produk
def clean_products(df):
    print("Cleaning products data...")
    return df.withColumn("harga", col("harga").cast("double")) \
            .dropDuplicates(["id_produk"]) \
            .withColumn("kategori_produk", trim(col("kategori_produk")))

# Fungsi untuk membersihkan data transaksi
def clean_transactions(df):
    print("Cleaning transactions data...")
    return df.withColumn("total_pembayaran", col("total_pembayaran").cast("double")) \
            .withColumn("banyak_cicilan", col("banyak_cicilan").cast("int")) \
            .withColumn("timestamp_pembelian", to_timestamp(col("timestamp_pembelian"), "yyyy-MM-dd HH:mm:ss")) \
            .withColumn("timestamp_persetujuan_toko", to_timestamp(col("timestamp_persetujuan_toko"), "yyyy-MM-dd HH:mm:ss")) \
            .withColumn("timestamp_pengiriman_ke_pelanggan", 
                      when(col("timestamp_pengiriman_ke_pelanggan").isNull(), lit(None)) \
                      .otherwise(to_timestamp(col("timestamp_pengiriman_ke_pelanggan"), "yyyy-MM-dd HH:mm:ss"))) \
            .withColumn("estimasi_sampai", 
                      when(col("estimasi_sampai").isNull(), lit(None)) \
                      .otherwise(to_date(col("estimasi_sampai"), "yyyy-MM-dd"))) \
            .dropDuplicates(["id_order"])

# Fungsi untuk membersihkan data order items
def clean_order_items(df):
    print("Cleaning order items data...")
    return df.withColumn("harga", col("harga").cast("double")) \
            .withColumn("jumlah", col("jumlah").cast("int")) \
            .withColumn("total_item", col("total_item").cast("double")) \
            .dropDuplicates(["id_order", "id_produk"])

# Fungsi untuk membersihkan data review
def clean_reviews(df):
    print("Cleaning reviews data...")
    return df.withColumn("nilai_rating_produk", col("nilai_rating_produk").cast("float")) \
            .withColumn("tanggal_review", to_date(col("tanggal_review"), "yyyy-MM-dd")) \
            .dropDuplicates(["id_pelanggan", "id_produk"])

# Fungsi untuk menyimpan data ke silver layer
def save_to_silver(df, table_name):
    print(f"Saving {table_name} data to silver layer...")
    df.write.mode("overwrite").parquet(f"{silver_path}/{table_name}")

# Main ETL Process
def run_etl():
    # Baca data dari bronze layer
    customers_df = read_bronze_data("customers")
    products_df = read_bronze_data("products")
    transactions_df = read_bronze_data("transactions")
    order_items_df = read_bronze_data("order_items")
    reviews_df = read_bronze_data("reviews")
    sellers_df = read_bronze_data("sellers")
    
    # Bersihkan data
    customers_clean = clean_customers(customers_df)
    products_clean = clean_products(products_df)
    transactions_clean = clean_transactions(transactions_df)
    order_items_clean = clean_order_items(order_items_df)
    reviews_clean = clean_reviews(reviews_df)
    
    # Simpan data ke silver layer
    save_to_silver(customers_clean, "customers")
    save_to_silver(products_clean, "products")
    save_to_silver(transactions_clean, "transactions")
    save_to_silver(order_items_clean, "order_items")
    save_to_silver(reviews_clean, "reviews")
    save_to_silver(sellers_df, "sellers")  # Sellers tidak perlu dibersihkan karena sudah bersih
    
    print("Bronze to Silver ETL completed!")

# Jalankan ETL
if __name__ == "__main__":
    run_etl()