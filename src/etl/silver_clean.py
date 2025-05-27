from pyspark.sql import SparkSession, functions as F

if __name__ == '__main__':
    spark = SparkSession.builder\
        .appName("SilverClean")\
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000")\
        .getOrCreate()

    # Baca Bronze
    df_tx    = spark.read.option("header",True).csv("/data/bronze/transactions/*.csv")
    df_items = spark.read.option("header",True).csv("/data/bronze/order_items/*.csv")
    df_prod  = spark.read.option("header",True).csv("/data/bronze/products/*.csv")

    # Konversi dan penamaan ulang
    df_tx = df_tx.withColumn("order_date", F.to_date("order_purchase_timestamp"))
    df_items = df_items.withColumn("quantity", F.col("order_item_quantity").cast("int"))
    df_prod = df_prod.withColumn("price", F.col("price").cast("double"))

    # Join: transaksi + order_items + products
    df_join = (
        df_tx.select("order_id","customer_id","order_date")
          .join(df_items, "order_id")
          .join(df_prod.select("product_id","price"), "product_id")
    )

    # Hitung total per baris
    df_clean = df_join.withColumn("total_amount", F.col("quantity") * F.col("price")).dropDuplicates()

    # Simpan ke Silver (Parquet)
    df_clean.write.mode("overwrite").parquet("/data/silver/sales_clean/")
    spark.stop()