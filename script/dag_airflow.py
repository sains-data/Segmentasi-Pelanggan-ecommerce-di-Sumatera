from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import logging
import sys
import os

# Path project, sesuaikan jika perlu
PROJECT_DIR = "/path/to/Segmentasi-Pelanggan-ecommerce-di-Sumatera"

default_args = {
    'owner': 'kelompok3',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 21),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_pyspark(script_name):
    script_path = os.path.join(PROJECT_DIR, 'scripts', script_name)
    cmd = f"spark-submit {script_path}"
    logging.info(f"Running command: {cmd}")
    os.system(cmd)

with DAG(
    'segmentasi_pipeline',
    default_args=default_args,
    description='ETL pipeline segmentasi pelanggan e-commerce di Sumatera',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    # Task 1: Data Ingestion ke Bronze Layer
    ingestion = BashOperator(
        task_id='data_ingestion',
        bash_command=f"python3 {os.path.join(PROJECT_DIR, 'scripts', 'ingest_data.py')}"
    )

    # Task 2: Data Cleansing & Transformasi ke Silver Layer
    cleansing = PythonOperator(
        task_id='data_cleansing',
        python_callable=run_pyspark,
        op_kwargs={'script_name': 'clean_transform.py'}
    )

    # Task 3: Clustering dan Penyimpanan ke Gold Layer
    clustering = PythonOperator(
        task_id='clustering',
        python_callable=run_pyspark,
        op_kwargs={'script_name': 'etl_clustering.py'}
    )

    ingestion >> cleansing >> clustering
