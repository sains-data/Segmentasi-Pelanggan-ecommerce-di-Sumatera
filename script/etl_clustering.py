from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.functions import col

# Inisialisasi Spark
spark = SparkSession.builder \
    .appName("ETL Clustering Pelanggan") \
    .enableHiveSupport() \
    .getOrCreate()

# Path input dari silver layer
df = spark.read.parquet("/silver/ecommerce_customers.parquet")

# Pra-pemrosesan: pastikan kolom numerik tidak null dan valid
df_valid = df.dropna(subset=["frekuensi_transaksi", "total_pembelian", "usia"])

# Vektorisasi fitur
assembler = VectorAssembler(
    inputCols=["frekuensi_transaksi", "total_pembelian", "usia"],
    outputCol="features_unscaled"
)
df_vector = assembler.transform(df_valid)

# Normalisasi fitur
scaler = StandardScaler(inputCol="features_unscaled", outputCol="features", withStd=True, withMean=True)
df_scaled = scaler.fit(df_vector).transform(df_vector)

# Evaluasi untuk menentukan jumlah cluster terbaik (K)
evaluator = ClusteringEvaluator(featuresCol="features", predictionCol="prediction", metricName="silhouette")
best_k = 2
best_score = -1

for k in range(2, 8):
    model = KMeans(k=k, seed=42, featuresCol="features").fit(df_scaled)
    predictions = model.transform(df_scaled)
    score = evaluator.evaluate(predictions)
    print(f"K={k}, Silhouette Score={score}")
    if score > best_score:
        best_score = score
        best_k = k

# Latih model dengan jumlah cluster terbaik
print(f"Menjalankan K-Means dengan K={best_k}...")
final_model = KMeans(k=best_k, seed=42, featuresCol="features").fit(df_scaled)
final_predictions = final_model.transform(df_scaled)

# Simpan hasil ke Hive (gold layer)
final_predictions.select(
    "id_pelanggan", "frekuensi_transaksi", "total_pembelian", "usia", "prediction"
).write.mode("overwrite").saveAsTable("gold.segmentasi_pelanggan")

print("Clustering selesai dan hasil disimpan ke Hive (gold.segmentasi_pelanggan).")

# Stop Spark
spark.stop()
