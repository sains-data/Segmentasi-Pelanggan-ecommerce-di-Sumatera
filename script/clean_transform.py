from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, regexp_replace, when

# Inisialisasi Spark
spark = SparkSession.builder \
    .appName("Clean & Transform E-Commerce Data") \
    .getOrCreate()

# Path input dan output
input_path = "/bronze/ecommerce_data.parquet"
output_path = "/silver/ecommerce_customers.parquet"

# Baca data dari bronze layer
df = spark.read.parquet(input_path)

# --- Cleaning ---
# Hilangkan baris dengan nilai null penting
df_clean = df.dropna(subset=["id_pelanggan", "id_order", "harga", "total_pembayaran", "timestamp_pembelian"])

# Bersihkan kolom angka dari karakter non-digit jika ada (contoh pada harga dan pembayaran)
df_clean = df_clean.withColumn("harga", regexp_replace(col("harga"), ",", "").cast("double"))
df_clean = df_clean.withColumn("total_pembayaran", regexp_replace(col("total_pembayaran"), ",", "").cast("double"))

# Ubah format tanggal
tanggal_cols = ["tanggal_review", "estimasi_sampai"]
for colname in tanggal_cols:
    df_clean = df_clean.withColumn(colname, to_date(col(colname), "yyyy-MM-dd"))

# Ganti nilai kosong pada kolom string tertentu dengan 'unknown'
string_cols = ["metode_pembayaran", "status_order", "kategori_produk"]
for c in string_cols:
    df_clean = df_clean.withColumn(c, when(col(c).isNull(), "unknown").otherwise(col(c)))

# --- Transformasi ---
# Hitung frekuensi transaksi dan total pembelian per pelanggan
df_agg = df_clean.groupBy("id_pelanggan").agg(
    {'id_order': 'count', 'total_pembayaran': 'sum'}
).withColumnRenamed("count(id_order)", "frekuensi_transaksi") \
 .withColumnRenamed("sum(total_pembayaran)", "total_pembelian")

# Ambil data demografis unik per pelanggan
df_demo = df_clean.select(
    "id_pelanggan", "usia", "provinsi_pelanggan", "kota_kabupaten_pelanggan"
).dropDuplicates(["id_pelanggan"])

# Gabungkan hasil agregasi dan data demografi
df_final = df_agg.join(df_demo, on="id_pelanggan", how="inner")

# Simpan ke silver layer
print("Menyimpan data bersih dan terstruktur ke silver layer...")
df_final.write.mode("overwrite").parquet(output_path)

print("Clean & transform selesai.")

# Stop Spark
spark.stop()
