from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
import os

# Inisialisasi Spark
spark = SparkSession.builder \
    .appName("Ingest Data Pelanggan") \
    .getOrCreate()

# Konfigurasi sumber data dan target HDFS
input_path = "data/raw/ecommerce_data.csv"  
output_path = "data/bronze/ecommerce_data.parquet"

# Cek apakah file input tersedia
if not os.path.exists(input_path):
    raise FileNotFoundError(f"File tidak ditemukan: {input_path}")

# Baca data CSV
print("Membaca file CSV...")
df = spark.read.option("header", True).option("inferSchema", True).csv(input_path)

# Tambahkan timestamp ingestion
df = df.withColumn("ingestion_time", current_timestamp())

# Tampilkan skema dan beberapa baris pertama
print("Skema Data:")
df.printSchema()
print("Contoh Data:")
df.show(5)

# Simpan ke HDFS dalam format Parquet
print(f"Menyimpan data ke bronze layer: {output_path}")
df.write.mode("overwrite").parquet(output_path)

print("Ingest data selesai.")

# Stop Spark
spark.stop()
