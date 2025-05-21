from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum, avg, datediff, month, year, dayofweek, date_format, when, lit, expr, round, desc, ntile
from pyspark.sql.window import Window
import os

# Inisialisasi Spark Session
spark = SparkSession.builder \
    .appName("Silver to Gold ETL") \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://hive-server:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Path HDFS
silver_path = "hdfs://namenode:9000/data/silver"
gold_path = "hdfs://namenode:9000/data/gold"

# Fungsi untuk membaca data dari silver layer
def read_silver_data(table_name):
    print(f"Reading {table_name} data from silver layer...")
    return spark.read.parquet(f"{silver_path}/{table_name}")

# Fungsi untuk menghitung metrics transaksi
def create_transaction_metrics(transactions_df, order_items_df):
    print("Creating transaction metrics...")
    
    # Join transactions dengan order items
    tx_items_df = transactions_df.join(
        order_items_df,
        on="id_order",
        how="inner"
    )
    
    # Hitung metrik per transaksi
    tx_metrics = tx_items_df.groupBy("id_order", "id_pelanggan", "timestamp_pembelian") \
        .agg(
            sum("total_item").alias("total_transaksi"),
            count("id_produk").alias("jumlah_item_berbeda"),
            avg("harga").alias("harga_rata_rata_item")
        ) \
        .withColumn("timestamp_pembelian_date", date_format("timestamp_pembelian", "yyyy-MM-dd")) \
        .withColumn("bulan_transaksi", month("timestamp_pembelian")) \
        .withColumn("tahun_transaksi", year("timestamp_pembelian")) \
        .withColumn("hari_transaksi", dayofweek("timestamp_pembelian"))
    
    return tx_metrics

# Fungsi untuk menghitung metrics pelanggan
def create_customer_metrics(transactions_df, order_items_df, customers_df):
    print("Creating customer metrics...")
    
    # Join transactions dengan order items
    tx_items_df = transactions_df.join(
        order_items_df,
        on="id_order",
        how="inner"
    )
    
    # Hitung metrik per pelanggan
    customer_metrics = tx_items_df.groupBy("id_pelanggan") \
        .agg(
            count("id_order").alias("jumlah_transaksi"),
            sum("total_item").alias("total_belanja"),
            avg("total_item").alias("rata_rata_belanja"),
            count(expr("distinct id_produk")).alias("jumlah_produk_berbeda")
        ) \
        .withColumn("nilai_belanja", round(col("total_belanja"), 2))
    
    # Hitung recency (diukur dari transaksi terakhir)
    latest_tx = transactions_df.groupBy("id_pelanggan") \
        .agg(expr("max(timestamp_pembelian)").alias("last_purchase_date"))
    
    # Join customer data
    customer_metrics = customer_metrics.join(latest_tx, on="id_pelanggan", how="left")
    customer_metrics = customer_metrics.join(customers_df, on="id_pelanggan", how="left")
    
    # Hitung segmen berdasarkan nilai belanja (quartile)
    windowSpec = Window.orderBy(desc("nilai_belanja"))
    customer_metrics = customer_metrics.withColumn("segmen_nilai", ntile(4).over(windowSpec))
    
    # Map nilai segmen
    customer_metrics = customer_metrics.withColumn(
        "segmen_pelanggan",
        when(col("segmen_nilai") == 1, "Platinum")
        .when(col("segmen_nilai") == 2, "Gold")
        .when(col("segmen_nilai") == 3, "Silver")
        .otherwise("Bronze")
    )
    
    return customer_metrics

# Fungsi untuk menghitung metrics produk
def create_product_metrics(order_items_df, products_df):
    print("Creating product metrics...")
    
    # Hitung metrik per produk
    product_metrics = order_items_df.groupBy("id_produk") \
        .agg(
            sum("jumlah").alias("jumlah_terjual"),
            sum("total_item").alias("total_penjualan"),
            avg("harga").alias("harga_rata_rata")
        )
    
    # Join dengan product data
    product_metrics = product_metrics.join(products_df, on="id_produk", how="left")
    
    # Hitung produk populer
    windowSpec = Window.partitionBy("kategori_produk").orderBy(desc("jumlah_terjual"))
    product_metrics = product_metrics.withColumn("peringkat_dalam_kategori", 
                                                expr("row_number() over (partition by kategori_produk order by jumlah_terjual desc)"))
    
    return product_metrics

# Fungsi untuk menghitung metrics regional
def create_regional_metrics(customers_df, customer_metrics):
    print("Creating regional metrics...")
    
    # Join dengan customer metrics
    regional_data = customers_df.join(customer_metrics, on="id_pelanggan", how="inner")
    
    # Agregasi per provinsi
    province_metrics = regional_data.groupBy("provinsi_pelanggan") \
        .agg(
            count("id_pelanggan").alias("jumlah_pelanggan"),
            sum("total_belanja").alias("total_belanja_provinsi"),
            avg("nilai_belanja").alias("rata_rata_belanja_provinsi")
        ) \
        .withColumn("rata_rata_belanja_provinsi", round(col("rata_rata_belanja_provinsi"), 2))
    
    # Agregasi per kota
    city_metrics = regional_data.groupBy("provinsi_pelanggan", "kota_kabupaten_pelanggan") \
        .agg(
            count("id_pelanggan").alias("jumlah_pelanggan"),
            sum("total_belanja").alias("total_belanja_kota"),
            avg("nilai_belanja").alias("rata_rata_belanja_kota")
        ) \
        .withColumn("rata_rata_belanja_kota", round(col("rata_rata_belanja_kota"), 2))
    
    return province_metrics, city_metrics

# Fungsi untuk menyimpan data ke gold layer
def save_to_gold(df, table_name):
    print(f"Saving {table_name} to gold layer...")
    df.write.mode("overwrite").parquet(f"{gold_path}/{table_name}")

# Main ETL Process
def run_etl():
    # Baca data dari silver layer
    customers_df = read_silver_data("customers")
    products_df = read_silver_data("products")
    transactions_df = read_silver_data("transactions")
    order_items_df = read_silver_data("order_items")
    reviews_df = read_silver_data("reviews")
    sellers_df = read_silver_data("sellers")
    
    # Buat metrics untuk analisis
    tx_metrics = create_transaction_metrics(transactions_df, order_items_df)
    customer_metrics = create_customer_metrics(transactions_df, order_items_df, customers_df)
    product_metrics = create_product_metrics(order_items_df, products_df)
    province_metrics, city_metrics = create_regional_metrics(customers_df, customer_metrics)
    
    # Simpan hasil metrics ke gold layer
    save_to_gold(tx_metrics, "transaction_metrics")
    save_to_gold(customer_metrics, "customer_metrics")
    save_to_gold(product_metrics, "product_metrics")
    save_to_gold(province_metrics, "province_metrics")
    save_to_gold(city_metrics, "city_metrics")
    
    # Buat view untuk analisis di Hive
    tx_metrics.createOrReplaceTempView("transaction_metrics_view")
    customer_metrics.createOrReplaceTempView("customer_metrics_view")
    product_metrics.createOrReplaceTempView("product_metrics_view")
    province_metrics.createOrReplaceTempView("province_metrics_view")
    city_metrics.createOrReplaceTempView("city_metrics_view")
    
    # Buat tabel di Hive untuk analisis
    spark.sql("CREATE DATABASE IF NOT EXISTS ecommerce_analytics")
    
    spark.sql("""
    CREATE TABLE IF NOT EXISTS ecommerce_analytics.transaction_metrics
    USING PARQUET
    AS SELECT * FROM transaction_metrics_view
    """)
    
    spark.sql("""
    CREATE TABLE IF NOT EXISTS ecommerce_analytics.customer_metrics
    USING PARQUET
    AS SELECT * FROM customer_metrics_view
    """)
    
    spark.sql("""
    CREATE TABLE IF NOT EXISTS ecommerce_analytics.product_metrics
    USING PARQUET
    AS SELECT * FROM product_metrics_view
    """)
    
    spark.sql("""
    CREATE TABLE IF NOT EXISTS ecommerce_analytics.province_metrics
    USING PARQUET
    AS SELECT * FROM province_metrics_view
    """)
    
    spark.sql("""
    CREATE TABLE IF NOT EXISTS ecommerce_analytics.city_metrics
    USING PARQUET
    AS SELECT * FROM city_metrics_view
    """)
    
    print("Silver to Gold ETL completed!")

# Jalankan ETL
if __name__ == "__main__":
    run_etl()