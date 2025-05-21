# Daftar File Script untuk Proyek Segmentasi Pelanggan

Berikut adalah daftar file script yang sebaiknya disiapkan untuk mendukung keseluruhan pipeline proyek segmentasi pelanggan e-commerce berbasis ekosistem Hadoop dan Spark.

---

## 1. `ingest_data.py`

**Fungsi:**

* Mengambil data dari API, file CSV, atau database menggunakan PyNiFi atau program ekstraksi manual.
* Menyimpan hasil ekstraksi ke bronze layer (HDFS).

**Output:** Parquet mentah di direktori `/bronze/`

---

## 2. `clean_transform.py`

**Fungsi:**

* Membersihkan data (null, duplikasi, format)
* Transformasi atribut (konversi tipe data, join antar tabel, normalisasi)
* Menyimpan data bersih ke silver layer (HDFS).

**Output:** Parquet terstandarisasi di `/silver/`

---

## 3. `etl_clustering.py`

**Fungsi:**

* Menyusun fitur untuk segmentasi pelanggan (frekuensi, nilai pembelian, usia)
* Melakukan standarisasi fitur dan clustering dengan K-Means (Spark MLlib)
* Menyimpan hasil ke gold layer dalam Hive.

**Output:** Tabel Hive `gold.segmentasi_pelanggan`

---

## 4. `load_superset.py` (opsional)

**Fungsi:**

* Menyiapkan koneksi dataset ke Superset
* Melakukan registrasi query segmentasi sebagai data source Superset (via API)

---

## 5. `dag_airflow.py`

**Fungsi:**

* Mendefinisikan DAG di Airflow untuk mengatur urutan eksekusi:

  1. Ingest ->
  2. Clean/Transform ->
  3. Clustering ->
  4. Validasi dan load hasil ke Hive

---

## 6. `test_pipeline.py`

**Fungsi:**

* Unit test dengan Pytest atau unittest untuk fungsi transformasi dan evaluasi cluster.
* Validasi format dan struktur DataFrame hasil intermediate.

---

Jika diperlukan, dapat juga ditambahkan:

* `utils.py` → fungsi bantu seperti konversi tanggal, cleaning modular
* `config.yaml` atau `.env` → konfigurasi direktori HDFS, nama tabel Hive, parameter Spark, dll.

---

Total File Script: **6 utama (+ 2 tambahan jika perlu)**
