from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, expr, sum as _sum, avg as _avg, \
    date_format, month, year, dayofweek, round, desc, when, ntile
from pyspark.sql.window import Window

# Inisialisasi Spark Session dengan Hive support dan konfigurasi yang benar
spark = SparkSession.builder \
    .appName("Silver to Gold ETL") \
    .enableHiveSupport() \
    .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
    .config("spark.hadoop.hive.metastore.uris", "thrift://hive-server:10000") \
    .getOrCreate()

# Paths HDFS
silver_path = "hdfs://namenode:9000/data/silver"
gold_path   = "hdfs://namenode:9000/data/gold"

def read_silver_data(table_name):
    print(f"▶ Reading '{table_name}' from silver layer")
    return spark.read.parquet(f"{silver_path}/{table_name}")

def create_transaction_metrics(transactions_df, order_items_df):
    print("▶ Creating transaction metrics")
    tx_items = transactions_df.join(order_items_df, on="id_order", how="inner")
    tx_metrics = tx_items.groupBy("id_order", "id_pelanggan", "timestamp_pembelian") \
        .agg(
            _sum("total_item").alias("total_transaksi"),
            count("id_produk").alias("jumlah_item_berbeda"),
            _avg("harga").alias("harga_rata_rata_item")
        ) \
        .withColumn("tanggal_transaksi", date_format("timestamp_pembelian", "yyyy-MM-dd")) \
        .withColumn("bulan_transaksi", month("timestamp_pembelian")) \
        .withColumn("tahun_transaksi", year("timestamp_pembelian")) \
        .withColumn("hari_transaksi", dayofweek("timestamp_pembelian"))
    return tx_metrics

def create_customer_metrics(transactions_df, order_items_df, customers_df):
    print("▶ Creating customer metrics")
    tx_items = transactions_df.join(order_items_df, on="id_order", how="inner")
    cust_metrics = tx_items.groupBy("id_pelanggan") \
        .agg(
            count("id_order").alias("jumlah_transaksi"),
            _sum("total_item").alias("total_belanja"),
            _avg("total_item").alias("rata_rata_belanja"),
            count(expr("distinct id_produk")).alias("jumlah_produk_berbeda")
        ) \
        .withColumn("nilai_belanja", round(col("total_belanja"), 2))

    latest = transactions_df.groupBy("id_pelanggan") \
        .agg(expr("max(timestamp_pembelian)").alias("last_purchase_date"))

    cust_metrics = cust_metrics.join(latest, on="id_pelanggan", how="left") \
        .join(customers_df, on="id_pelanggan", how="left")

    win = Window.orderBy(desc("nilai_belanja"))
    cust_metrics = cust_metrics.withColumn("segmen_nilai", ntile(4).over(win)) \
        .withColumn("segmen_pelanggan",
            when(col("segmen_nilai") == 1, "Platinum")
           .when(col("segmen_nilai") == 2, "Gold")
           .when(col("segmen_nilai") == 3, "Silver")
           .otherwise("Bronze")
        )
    return cust_metrics

def create_product_metrics(order_items_df, products_df):
    print("▶ Creating product metrics")
    prod_metrics = order_items_df.groupBy("id_produk") \
        .agg(
            _sum("jumlah").alias("jumlah_terjual"),
            _sum("total_item").alias("total_penjualan"),
            _avg("harga").alias("harga_rata_rata")
        ) \
        .join(products_df, on="id_produk", how="left")

    win = Window.partitionBy("kategori_produk").orderBy(desc("jumlah_terjual"))
    prod_metrics = prod_metrics.withColumn(
        "peringkat_dalam_kategori",
        expr("row_number() over (partition by kategori_produk order by jumlah_terjual desc)")
    )
    return prod_metrics

def create_regional_metrics(customers_df, customer_metrics):
    print("▶ Creating regional metrics")
    reg = customers_df.join(customer_metrics, on="id_pelanggan", how="inner")
    
    province = reg.groupBy("provinsi_pelanggan") \
        .agg(
            count("id_pelanggan").alias("jumlah_pelanggan"),
            _sum("total_belanja").alias("total_belanja_provinsi"),
            _avg("nilai_belanja").alias("rata_rata_belanja_provinsi")
        ) \
        .withColumn("rata_rata_belanja_provinsi", round(col("rata_rata_belanja_provinsi"), 2))

    city = reg.groupBy("provinsi_pelanggan", "kota_kabupaten_pelanggan") \
        .agg(
            count("id_pelanggan").alias("jumlah_pelanggan"),
            _sum("total_belanja").alias("total_belanja_kota"),
            _avg("nilai_belanja").alias("rata_rata_belanja_kota")
        ) \
        .withColumn("rata_rata_belanja_kota", round(col("rata_rata_belanja_kota"), 2))

    return province, city

def save_to_gold(df, name):
    print(f"▶ Writing '{name}' to gold layer")
    df.write.mode("overwrite").parquet(f"{gold_path}/{name}")

def run_etl():
    # Baca semua silver table
    customers    = read_silver_data("customers")
    products     = read_silver_data("products")
    transactions = read_silver_data("transactions")
    order_items  = read_silver_data("order_items")

    # Hitung metrics
    tx_metrics      = create_transaction_metrics(transactions, order_items)
    cust_metrics    = create_customer_metrics(transactions, order_items, customers)
    prod_metrics    = create_product_metrics(order_items, products)
    province_metrics, city_metrics = create_regional_metrics(customers, cust_metrics)

    # Simpan ke Gold
    save_to_gold(tx_metrics,      "transaction_metrics")
    save_to_gold(cust_metrics,    "customer_metrics")
    save_to_gold(prod_metrics,    "product_metrics")
    save_to_gold(province_metrics,"province_metrics")
    save_to_gold(city_metrics,    "city_metrics")

    # Juga buat Hive tables untuk analisis SQL
    spark.sql("CREATE DATABASE IF NOT EXISTS ecommerce_analytics")
    for tbl in ["transaction_metrics", "customer_metrics", "product_metrics", "province_metrics", "city_metrics"]:
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS ecommerce_analytics.{tbl}
            USING PARQUET
            LOCATION '{gold_path}/{tbl}'
        """)
    print("✅ Silver to Gold ETL completed!")

if __name__ == "__main__":
    run_etl()
