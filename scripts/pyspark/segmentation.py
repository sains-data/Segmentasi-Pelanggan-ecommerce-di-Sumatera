from pyspark.sql import SparkSession
from pyspark.sql.functions import col #, collect_list, struct, array (tidak digunakan di kode Anda)
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
# import numpy as np # tidak digunakan
# import matplotlib.pyplot as plt # Dihapus untuk headless run
from pyspark.ml import Pipeline

# Path HDFS (sesuai skrip Anda)
gold_path = "hdfs://namenode:9000/data/gold"
model_path = "hdfs://namenode:9000/models"

def load_customer_data(spark):
    """Load customer metrics data from gold layer"""
    print("Loading customer metrics data...")
    # Pastikan ada kolom customer_id atau identifier unik pelanggan
    return spark.read.parquet(f"{gold_path}/customer_metrics")

def prepare_features(customer_df):
    """Prepare features for customer segmentation"""
    print("Preparing features for segmentation...")
    
    # Seleksi fitur untuk segmentasi
    # Pastikan kolom ini ada di customer_df hasil ETL
    selected_features = ["jumlah_transaksi", "total_belanja", "rata_rata_belanja", "jumlah_produk_berbeda"]
    
    # Cek apakah semua selected_features ada di customer_df
    missing_cols = [f for f in selected_features if f not in customer_df.columns]
    if missing_cols:
        print(f"Error: Kolom berikut tidak ditemukan di customer_metrics: {missing_cols}")
        print(f"Kolom yang tersedia: {customer_df.columns}")
        raise ValueError(f"Kolom fitur hilang: {missing_cols}")

    # Membuat vector features
    assembler = VectorAssembler(
        inputCols=selected_features, 
        outputCol="features",
        handleInvalid="skip" # Atau "error" atau "keep"
    )
    
    # Standardisasi fitur
    scaler = StandardScaler(
        inputCol="features", 
        outputCol="scaled_features",
        withStd=True, 
        withMean=True
    )
    
    # Membuat pipeline untuk preprocessing
    pipeline = Pipeline(stages=[assembler, scaler])
    
    # Fit dan transform data
    print("Fitting preprocessing pipeline...")
    pipeline_model = pipeline.fit(customer_df)
    print("Transforming data with preprocessing pipeline...")
    prepared_data = pipeline_model.transform(customer_df)
    
    # Filter baris di mana scaled_features mungkin null (jika handleInvalid="skip" menghasilkan null)
    prepared_data = prepared_data.filter(col("scaled_features").isNotNull())
    print(f"Jumlah data setelah preprocessing dan filter null scaled_features: {prepared_data.count()}")
    if prepared_data.count() == 0:
        print("Error: Tidak ada data yang tersisa setelah preprocessing. Periksa input data dan handleInvalid.")
        raise ValueError("Tidak ada data valid setelah preprocessing.")
        
    return prepared_data, pipeline_model

def find_optimal_k(data, max_k=10):
    """Find optimal number of clusters using silhouette score"""
    print(f"Finding optimal k (2-{max_k}) using Silhouette Score...")
    
    evaluator = ClusteringEvaluator(
        predictionCol="prediction", 
        featuresCol="scaled_features", 
        metricName="silhouette"
    )
    
    silhouette_scores = []
    
    for k_val in range(2, max_k + 1):
        print(f"Trying k={k_val}...")
        kmeans = KMeans(
            k=k_val, 
            seed=42, 
            featuresCol="scaled_features", 
            predictionCol="prediction"
        )
        try:
            model = kmeans.fit(data)
            predictions = model.transform(data)
            
            silhouette = evaluator.evaluate(predictions)
            silhouette_scores.append(silhouette)
            
            print(f"k={k_val}, Silhouette={silhouette}")
        except Exception as e:
            print(f"Error saat mencoba k={k_val}: {e}")
            silhouette_scores.append(-1) # Skor buruk jika error

    if not silhouette_scores or max(silhouette_scores) == -1 : # Handle jika semua k gagal
        print("Tidak dapat menentukan optimal k karena semua percobaan gagal atau tidak ada skor valid.")
        print("Menggunakan default k=3.")
        return 3

    optimal_k_val = silhouette_scores.index(max(silhouette_scores)) + 2 # +2 karena range dimulai dari 2
    
    print(f"Based on silhouette analysis, optimal k = {optimal_k_val}")
    
    # Kode plotting WSSSE dan Silhouette dihapus karena tidak akan render di spark-submit
    # Visualisasi bisa dilakukan di Jupyter Notebook secara terpisah jika diperlukan
    
    return optimal_k_val

def train_kmeans_model(data, k_val):
    """Train KMeans model with the specified number of clusters"""
    print(f"Training KMeans model with k={k_val}...")
    
    kmeans = KMeans(
        k=k_val, 
        seed=42, 
        featuresCol="scaled_features", 
        predictionCol="cluster" # Kolom output cluster
    )
    
    model = kmeans.fit(data)
    
    return model

def interpret_clusters(data_with_features, model):
    """Interpret the resulting clusters"""
    print("Interpreting clusters...")
    
    # Get cluster assignments
    # data_with_features sudah punya 'scaled_features'
    # model.transform akan menambahkan kolom 'cluster'
    result_df = model.transform(data_with_features)
    
    # Calculate cluster statistics
    # Kolom asli (sebelum di-scale) lebih mudah diinterpretasi untuk rata-rata
    # Kita perlu join kembali dengan data sebelum scaling atau pastikan kolom asli ada
    # Asumsikan 'data_with_features' masih memiliki kolom asli seperti "jumlah_transaksi", dll.
    # Jika tidak, perlu di-select dari DataFrame sebelum 'scaled_features' dibuat.
    
    # Ambil kolom asli dari 'data_with_features' yang digunakan untuk membuat 'features' (sebelum scaling)
    # VectorAssembler menyimpan inputCols di metadata, tapi lebih mudah jika kita tahu nama kolomnya.
    original_feature_cols = ["jumlah_transaksi", "total_belanja", "rata_rata_belanja", "jumlah_produk_berbeda", "customer_id"]
    
    # Pastikan kolom-kolom ini ada di result_df
    cols_to_check = original_feature_cols + ["cluster"]
    available_cols_for_interpretation = [c for c in cols_to_check if c in result_df.columns]
    
    if "customer_id" not in result_df.columns:
        print("Warning: customer_id tidak ditemukan di result_df untuk interpretasi.")
    
    # Hitung jumlah dan rata-rata metrik per cluster
    # Hanya gunakan kolom yang ada untuk agg
    agg_exprs = [col("customer_id").alias("NumCustomers")] # Hitung jumlah pelanggan
    for f_col in original_feature_cols:
        if f_col in result_df.columns and f_col != "customer_id":
            agg_exprs.append(col(f_col).alias(f"Avg{f_col.capitalize()}"))
            
    if len(agg_exprs) > 1: # Jika ada fitur selain NumCustomers
      cluster_summary = result_df.groupBy("cluster").agg(
          countDistinct("customer_id").alias("NumCustomers"), # Jumlah pelanggan unik
          avg("jumlah_transaksi").alias("AvgJumlahTransaksi"),
          avg("total_belanja").alias("AvgTotalBelanja"),
          avg("rata_rata_belanja").alias("AvgRataRataBelanja"),
          avg("jumlah_produk_berbeda").alias("AvgJumlahProdukBerbeda")
      ).orderBy("cluster")
    else:
      cluster_summary = result_df.groupBy("cluster").agg(countDistinct("customer_id").alias("NumCustomers")).orderBy("cluster")


    # Print cluster centers (dari fitur yang di-scale)
    centers = model.clusterCenters()
    print("Cluster centers (scaled features):")
    for i, center in enumerate(centers):
        print(f"Cluster {i} center: {center}")
    
    return result_df, cluster_summary # Mengembalikan result_df dan cluster_summary

def save_segmentation_results(spark, segmented_data_df):
    """Save segmentation results to HDFS and Hive"""
    print("Saving segmentation results...")
    
    # Pilih kolom yang akan disimpan (termasuk customer_id dan cluster)
    # Pastikan 'customer_id' ada di segmented_data_df
    if "customer_id" not in segmented_data_df.columns:
        print("Error: 'customer_id' tidak ada di DataFrame hasil segmentasi. Tidak bisa menyimpan.")
        # Coba ambil dari kolom lain jika ada, misal 'customer_unique_id'
        # Atau pastikan 'customer_id' dibawa terus dari awal.
        # Untuk sekarang, kita asumsikan 'customer_id' ada.
        raise ValueError("'customer_id' tidak ditemukan untuk disimpan.")

    output_df = segmented_data_df.select(
        "customer_id", # Identifier pelanggan
        "jumlah_transaksi", 
        "total_belanja", 
        "rata_rata_belanja", 
        "jumlah_produk_berbeda",
        "cluster" # Kolom hasil segmentasi
    )
    
    # Simpan ke HDFS Parquet
    output_df.write.mode("overwrite").parquet(f"{gold_path}/customer_segments")
    print(f"Hasil segmentasi disimpan ke HDFS: {gold_path}/customer_segments")
    
    # Buat tabel Hive
    output_df.createOrReplaceTempView("customer_segments_view")
    
    # Buat database jika belum ada
    spark.sql("CREATE DATABASE IF NOT EXISTS ecommerce_analytics")
    print("Database 'ecommerce_analytics' dipastikan ada.")
    
    # Buat tabel Hive dari view
    # Nama tabel di Hive tidak boleh ada slash
    hive_table_name = "ecommerce_analytics.customer_segments_table" # Ganti nama agar valid
    print(f"Membuat atau mengganti tabel Hive: {hive_table_name}")
    spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {hive_table_name}
    (
        customer_id STRING,
        jumlah_transaksi BIGINT,
        total_belanja DOUBLE,
        rata_rata_belanja DOUBLE,
        jumlah_produk_berbeda BIGINT,
        cluster INT
    )
    USING PARQUET
    LOCATION '{gold_path}/customer_segments' 
    """) 
    # Atau jika ingin Spark mengelola data di warehouse Hive:
    # spark.sql(f"DROP TABLE IF EXISTS {hive_table_name}") # Hapus dulu jika ingin create as select
    # spark.sql(f"""
    # CREATE TABLE {hive_table_name}
    # USING PARQUET
    # AS SELECT * FROM customer_segments_view
    # """)
    
    print("Segmentation results saved successfully to HDFS and Hive Metastore!")

def save_model_artifacts(model_to_save, pipeline_model_to_save):
    """Save the trained model and preprocessing pipeline"""
    print("Saving models...")
    
    # Save KMeans model
    kmeans_model_path_hdfs = f"{model_path}/kmeans_customer_segmentation"
    model_to_save.write().overwrite().save(kmeans_model_path_hdfs) # Gunakan write().overwrite()
    print(f"KMeans model saved to: {kmeans_model_path_hdfs}")
    
    # Save preprocessing pipeline
    pipeline_model_path_hdfs = f"{model_path}/preprocessing_pipeline"
    pipeline_model_to_save.write().overwrite().save(pipeline_model_path_hdfs) # Gunakan write().overwrite()
    print(f"Preprocessing pipeline saved to: {pipeline_model_path_hdfs}")
    
    print("Models saved successfully!")

def run_segmentation_pipeline(spark_session):
    """Run the complete customer segmentation process"""
    # Load data
    customer_data_df = load_customer_data(spark_session)
    if customer_data_df.count() == 0:
        print("Tidak ada data customer_metrics yang dimuat. Proses dihentikan.")
        return

    # Prepare features
    prepared_data_df, pipeline_model = prepare_features(customer_data_df)
    if prepared_data_df.count() == 0:
        print("Tidak ada data yang tersisa setelah preprocessing. Proses dihentikan.")
        return
        
    # Find optimal k
    optimal_k_value = find_optimal_k(prepared_data_df, max_k=8) # Batasi max_k untuk kecepatan
    
    # Train KMeans model
    kmeans_model = train_kmeans_model(prepared_data_df, optimal_k_value)
    
    # Interpret clusters
    # Kita perlu data dengan fitur asli untuk interpretasi yang lebih baik
    # prepared_data_df sudah berisi kolom asli dan scaled_features
    segmented_output_df, cluster_stats_df, cluster_avgs_df = interpret_clusters(prepared_data_df, kmeans_model)
    
    # Display results
    print("\nCluster statistics (Jumlah Pelanggan per Segmen):")
    if cluster_stats_df: # Jika cluster_stats_df tidak None
        cluster_stats_df.show()
    
    print("\nCluster average metrics:")
    if cluster_avgs_df: # Jika cluster_avgs_df tidak None
        cluster_avgs_df.show(truncate=False)
    
    # Save results
    save_segmentation_results(spark_session, segmented_output_df)
    
    # Save model
    save_model_artifacts(kmeans_model, pipeline_model)
    
    print("Customer segmentation completed successfully!")

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("CustomerSegmentationWithHive") \
        .config("spark.sql.warehouse.dir", "hdfs://namenode:9000/user/hive/warehouse") \
        .config("hive.metastore.uris", "thrift://hive-metastore:9083") \
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
        .enableHiveSupport() \
        .getOrCreate()

    run_segmentation_pipeline(spark)

    spark.stop()