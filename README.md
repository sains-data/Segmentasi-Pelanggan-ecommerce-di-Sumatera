# 🚀 Segmentasi Pelanggan E-Commerce di Sumatera dengan Ekosistem Hadoop

## 📖 Deskripsi Singkat
Repositori ini adalah hasil proyek Big Data Analytics berjudul **"Implementasi Ekosistem Hadoop untuk Analisis Segmentasi Pelanggan E-Commerce di Sumatera"** oleh Kelompok 3, Program Studi Sains Data, Institut Teknologi Sumatera.

## 🗂️ Daftar Isi

* [Latar Belakang](#latar-belakang)
* [Arsitektur Sistem](#arsitektur-sistem)
* [Teknologi yang Digunakan](#teknologi-yang-digunakan)
* [Pipeline Proyek](#pipeline-proyek)
* [Struktur Direktori](#struktur-direktori)
* [Cara Menjalankan](#cara-menjalankan)
* [Dataset](#dataset)
* [Hasil Visualisasi](#hasil-visualisasi)
* [Tim Pengembang](#tim-pengembang)

## 📝 Latar Belakang

Proyek ini bertujuan untuk menganalisis segmentasi pelanggan e-commerce di pulau Sumatera berdasarkan data transaksi dan demografi. Analisis dilakukan dalam lingkungan Hadoop yang terdiri dari berbagai komponen seperti Spark, Hive, dan NiFi. Sistem ini menggunakan pendekatan **data lake** dan **arsitektur medallion** (bronze, silver, gold layer) untuk mengelola pipeline data secara batch.

## 🏗️ Arsitektur Sistem

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

## 🛠️ Teknologi yang Digunakan



[![Hadoop 3.4.1](https://img.shields.io/badge/Hadoop-3.4.1-yellow?logo=apachehadoop)](https://hadoop.apache.org/releases.html)   
[![Spark 3.5.5](https://img.shields.io/badge/Spark-3.5.5-orange?logo=apachespark)](https://spark.apache.org/downloads.html)    
[![Hive 4.0.1](https://img.shields.io/badge/Hive-4.0.1-yellowgreen?logo=apachehive)](https://hive.apache.org/general/downloads/)    
[![NiFi 2.4.0](https://img.shields.io/badge/NiFi-2.4.0-blue?logo=apachenifi)](https://nifi.apache.org/download.html)    
[![Oozie 5.2.1](https://img.shields.io/badge/Oozie-5.2.1-red?logo=apacheoozie)](https://oozie.apache.org/downloads.html)    
[![Airflow 2.6.0](https://img.shields.io/badge/Airflow-2.6.0-blue?logo=apacheairflow)](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html)  
[![Atlas 2.4](https://img.shields.io/badge/Atlas-2.4-lightgrey?logo=apacheatlas)](https://atlas.apache.org/Downloads.html)   
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://www.python.org/downloads/release/python-3100/)   
[![Docker Latest](https://img.shields.io/badge/Docker-Latest-blue?logo=docker)](https://www.docker.com/products/docker-desktop/)   

## 🔄 Pipeline Proyek

1. **Data Ingestion**: Mengambil data transaksi dan demografi pelanggan menggunakan NiFi/Sqoop ke bronze layer HDFS.
2. **Data Cleansing**: Membersihkan data dan transformasi pada silver layer dengan PySpark.
3. **Data Enrichment**: Menambahkan atribut demografi dan menghitung metrik pelanggan.
4. **Clustering**: Segmentasi pelanggan menggunakan K-Means di Spark MLlib.
5. **Data Aggregation**: Menyimpan hasil di gold layer sebagai tabel Hive.
6. **Visualisasi**: Dashboard Superset untuk menggambarkan karakteristik tiap segmen.

## 📁 Struktur Direktori

```
📁 data/                   # Dataset & hasil pre-processing
📁 notebooks/              # Notebook eksplorasi & EDA
📁 scripts/                # Skrip PySpark & pipeline
📁 airflow_dags/           # DAG Airflow untuk orkestrasi
📄 docker-compose.yml      # Setup container Hadoop ecosystem
📁 hive/                   # Query Hive & definisi skema
📁 visualizations/         # Gambar dashboard & visualisasi
📁 tests/                  # Unit test pipeline Spark
📄 README.md               # Dokumentasi proyek

```

## ▶️ Cara Menjalankan

**1. Clone repositori:**

```bash
git clone https://github.com/sains-data/Segmentasi-Pelanggan-ecommerce-di-Sumatera.git
cd Segmentasi-Pelanggan-ecommerce-di-Sumatera
```

**2. Jalankan Docker Compose:**

```bash
docker-compose up -d
```

**3. Akses layanan melalui URL:**

* NiFi: `http://localhost:8080`
* Hive: `http://localhost:10000`
* Superset: `http://localhost:8088`

**4. Jalankan pipeline ETL:**

* DAG Airflow `segmentasi_pipeline`
* Skrip PySpark: `scripts/clustering.py`

## 📊 Dataset

Dataset terdiri dari 19 kolom yang mencakup informasi transaksi, demografi, lokasi, dan waktu. Contoh kolom:

* `id_pelanggan`, `provinsi_pelanggan`, `harga`, `total_pembayaran`, `kategori_produk`, `status_order`, `timestamp_pembelian`, dll.

## 📈 Hasil Visualisasi

Visualisasi dilakukan di Apache Superset. Insight meliputi:

* Segmentasi berdasarkan provinsi
* Nilai pembelian tertinggi per segmen
* Frekuensi transaksi dan demografi pelanggan

## 👨‍💻 Tim Pengembang

Kelompok 3 - Sains Data ITERA:

* <a href="https://github.com/khoirulmizan" target="_blank"> <img src="https://github.com/khoirulmizan.png" width="20" height="20" alt="Khoirul Mizan Abdullah" title="Khoirul Mizan Abdullah" style="border-radius:50%; margin-right:10px;"> </a> Khoirul Mizan Abdullah - 122450010 
* <a href="https://github.com/kharisaharvanny" target="_blank"> <img src="https://github.com/kharisaharvanny.png" width="20" height="20" alt="Kharisa Harvanny" title="Kharisa Harvanny" style="border-radius:50%; margin-right:10px;"> </a>Kharisa Harvanny - 122450061 
* <a href="https://github.com/strng-fer" target="_blank"> <img src="https://github.com/strng-fer.png" width="20" height="20" alt="Feryadi Yulius" title="Feryadi Yulius" style="border-radius:50%; margin-right:10px;"> </a> Feryadi Yulius - 122450087 
* <a href="https://github.com/zeeyachan" target="_blank"> <img src="https://github.com/zeeyachan.png" width="20" height="20" alt="Nabila Zakiyah Zahra" title="Nabila Zakiyah Zahra" style="border-radius:50%; margin-right:10px;"> </a> Nabila Zakiyah Zahra - 122450139 
* <a href="https://github.com/Wildozen" target="_blank"> <img src="https://github.com/Wildozen.png" width="20" height="20" alt="Yosia Adwily Nainggolan" title="Yosia Adwily Nainggolan" style="border-radius:50%; margin-right:10px;"> </a> Yosia Adwily Nainggolan - 121450063 

---

Lisensi dan informasi tambahan dapat disesuaikan berdasarkan kebutuhan. Untuk pertanyaan atau kontribusi, silakan ajukan issue atau pull request melalui GitHub.
