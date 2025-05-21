import requests
import json
import os

# Konfigurasi koneksi Superset API
SUPERSET_HOST = os.getenv("SUPERSET_HOST", "http://localhost:8088")
USERNAME = os.getenv("SUPERSET_USERNAME", "admin")
PASSWORD = os.getenv("SUPERSET_PASSWORD", "admin")

# 1. Login dan ambil access token
login_url = f"{SUPERSET_HOST}/api/v1/security/login"
headers = {"Content-Type": "application/json"}

payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "provider": "db",
    "refresh": True
}

login_response = requests.post(login_url, json=payload, headers=headers)
if login_response.status_code != 200:
    raise Exception("Gagal login ke Superset API")

access_token = login_response.json()["access_token"]
headers_auth = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# 2. Registrasi koneksi database (Hive/Presto/Trino/Spark SQL)
database_payload = {
    "database_name": "Hive Segmentasi",
    "sqlalchemy_uri": "hive://hive@hive-server:10000/default"
}

db_response = requests.post(f"{SUPERSET_HOST}/api/v1/database/", json=database_payload, headers=headers_auth)
if db_response.status_code not in [200, 201]:
    print("Koneksi database mungkin sudah terdaftar atau gagal ditambahkan.")
else:
    print("Berhasil menambahkan koneksi database ke Superset.")

# 3. Daftarkan dataset dari tabel Hive gold.segmentasi_pelanggan
dataset_payload = {
    "database": 1,  # ID database, perlu disesuaikan jika tidak otomatis 1
    "schema": "gold",
    "table_name": "segmentasi_pelanggan"
}

ds_response = requests.post(f"{SUPERSET_HOST}/api/v1/dataset/", json=dataset_payload, headers=headers_auth)
if ds_response.status_code not in [200, 201]:
    print("Dataset mungkin sudah terdaftar atau gagal didaftarkan.")
else:
    print("Dataset berhasil diregistrasi di Superset.")