from pyspark.sql import SparkSession

def run_query_analysis(spark):
    print("Memulai query dan analisis hasil segmentasi dari Hive...")

    hive_table_name = "ecommerce_analytics.customer_segments_table"

    try:
        print(f"Membaca data segmentasi dari tabel Hive: {hive_table_name}")
        # Cek apakah tabel ada
        spark.sql(f"SHOW TABLES IN ecommerce_analytics LIKE 'customer_segments_table'").show()
        
        segments_df = spark.table(hive_table_name)
        segments_df.printSchema()
        print(f"Jumlah baris di tabel {hive_table_name}: {segments_df.count()}")
        if segments_df.count() == 0:
            print(f"Tidak ada data di tabel {hive_table_name}. Analisis tidak dapat dilanjutkan.")
            return
            
    except Exception as e:
        print(f"Error saat membaca data dari Hive: {e}")
        return

    print("\nContoh Query dari Tabel Hive:")

    # 1. Jumlah pelanggan per segmen
    print("\n--- Jumlah Pelanggan per Segmen ---")
    segments_df.groupBy("cluster") \
        .count() \
        .withColumnRenamed("count", "JumlahPelanggan") \
        .orderBy("cluster") \
        .show()

    # 2. Rata-rata metrik (yang disimpan) per Segmen
    print("\n--- Rata-rata Metrik per Segmen ---")
    segments_df.groupBy("cluster") \
        .avg("jumlah_transaksi", "total_belanja", "rata_rata_belanja", "jumlah_produk_berbeda") \
        .orderBy("cluster") \
        .show(truncate=False)
    
    # 3. Contoh: Pelanggan dengan total belanja tertinggi di setiap segmen
    print("\n--- Pelanggan dengan Total Belanja Tertinggi per Segmen (Contoh) ---")
    # Ini memerlukan window function jika ingin top N, atau subquery.
    # Untuk kesederhanaan, kita tampilkan beberapa pelanggan dari segmen tertentu.
    if segments_df.filter(col("cluster") == 0).count() > 0:
        segments_df.filter(col("cluster") == 0) \
            .orderBy(col("total_belanja").desc()) \
            .select("customer_id", "total_belanja", "cluster") \
            .show(5, truncate=False)
    else:
        print("Tidak ada data untuk segmen 0.")


    print("Query dan analisis selesai.")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("SegmentationQueryAnalysisHive") \
        .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
        .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
        .enableHiveSupport() \
        .getOrCreate()

    run_query_analysis(spark)

    spark.stop()