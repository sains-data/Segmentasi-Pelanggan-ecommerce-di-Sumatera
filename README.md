# Segmentasi Pelanggan E-Commerce di Sumatera dengan Ekosistem Hadoop

Repositori ini merupakan hasil implementasi proyek Analisis Big Data dengan judul **"Implementasi Ekosistem Hadoop untuk Analisis Segmentasi Pelanggan E-Commerce di Sumatera"** oleh Kelompok 3 - Program Studi Sains Data, Institut Teknologi Sumatera.

## Daftar Isi

* [Latar Belakang](#latar-belakang)
* [Arsitektur Sistem](#arsitektur-sistem)
* [Teknologi yang Digunakan](#teknologi-yang-digunakan)
* [Pipeline Proyek](#pipeline-proyek)
* [Struktur Direktori](#struktur-direktori)
* [Cara Menjalankan](#cara-menjalankan)
* [Dataset](#dataset)
* [Hasil Visualisasi](#hasil-visualisasi)
* [Tim Pengembang](#tim-pengembang)

## Latar Belakang

Proyek ini bertujuan untuk menganalisis segmentasi pelanggan e-commerce di pulau Sumatera berdasarkan data transaksi dan demografi. Analisis dilakukan dalam lingkungan Hadoop yang terdiri dari berbagai komponen seperti Spark, Hive, dan NiFi. Sistem ini menggunakan pendekatan data lake dan arsitektur medallion (bronze, silver, gold layer) untuk mengelola pipeline data secara batch.

## Arsitektur Sistem

Arsitektur sistem dibangun di atas Docker multi-container dengan 6 VM:

* 2 Master Node (NameNode, ResourceManager, NiFi, Airflow, Atlas)
* 4 Worker Node (DataNode, NodeManager, Spark Executor)

Sistem menggunakan:

* **Apache Hadoop** untuk penyimpanan terdistribusi (HDFS)
* **Apache Spark** untuk pemrosesan batch
* **Apache NiFi** dan **Sqoop** untuk ekstraksi data
* **Apache Hive** untuk query dan penyimpanan terstruktur
* **Apache Airflow & Oozie** untuk orkestrasi workflow
* **Apache Atlas** untuk data lineage
* **Superset/PowerBI** untuk visualisasi hasil

## Teknologi yang Digunakan

| Komponen | Versi |
| -------- | ----- |
| Hadoop   | 3.4.1 |
| Spark    | 3.5.5 |
| Hive     | 4.0.1 |
| NiFi     | 2.4.0 |
| Oozie    | 5.2.1 |
| Airflow  | 2.6.0 |
| Atlas    | 2.4   |
| Python   | 3.10  |
| Docker   | -     |

## Pipeline Proyek

1. **Data Ingestion**: Mengambil data transaksi dan demografi pelanggan menggunakan NiFi/Sqoop ke bronze layer HDFS.
2. **Data Cleansing**: Membersihkan data dan transformasi pada silver layer dengan PySpark.
3. **Data Enrichment**: Menambahkan atribut demografi dan menghitung metrik pelanggan.
4. **Clustering**: Segmentasi pelanggan menggunakan K-Means di Spark MLlib.
5. **Data Aggregation**: Menyimpan hasil di gold layer sebagai tabel Hive.
6. **Visualisasi**: Dashboard Superset untuk menggambarkan karakteristik tiap segmen.

## Struktur Direktori

```
├── data/                   # Dataset dan hasil pre-processing
├── notebooks/              # Notebook eksplorasi awal dan EDA
├── scripts/                # Skrip PySpark dan pipeline
├── airflow_dags/          # DAG Airflow untuk orkestrasi
├── docker-compose.yml     # Setup container Hadoop ecosystem
├── hive/                  # Query Hive dan definisi skema
├── visualizations/        # File dashboard/visualisasi
├── tests/                 # Unit test Spark pipeline
└── README.md              # Dokumentasi proyek
```

## Cara Menjalankan

1. Clone repositori:

```bash
git clone https://github.com/sains-data/bigdata-spark.git
cd bigdata-spark
```

2. Jalankan Docker Compose:

```bash
docker-compose up -d
```

3. Akses layanan melalui URL:

* NiFi: `http://localhost:8080`
* Hive: `http://localhost:10000`
* Superset: `http://localhost:8088`

4. Jalankan pipeline ETL:

* DAG Airflow `segmentasi_pipeline`
* Skrip PySpark: `scripts/clustering.py`

## Dataset

Dataset terdiri dari 19 kolom yang mencakup informasi transaksi, demografi, lokasi, dan waktu. Contoh kolom:

* `id_pelanggan`, `provinsi_pelanggan`, `harga`, `total_pembayaran`, `kategori_produk`, `status_order`, `timestamp_pembelian`, dll.

## Hasil Visualisasi

Visualisasi dilakukan di Apache Superset. Insight meliputi:

* Segmentasi berdasarkan provinsi
* Nilai pembelian tertinggi per segmen
* Frekuensi transaksi dan demografi pelanggan

## Tim Pengembang

Kelompok 3 - Sains Data ITERA:

* Khoirul Mizan Abdullah - 122450010
* Kharisa Harvanny - 122450061
* Feryadi Yulius - 122450087
* Nabila Zakiyah Zahra - 122450139
* Yosia Adwily Nainggolan - 121450063

---

Lisensi dan informasi tambahan dapat disesuaikan berdasarkan kebutuhan. Untuk pertanyaan atau kontribusi, silakan ajukan issue atau pull request melalui GitHub.
