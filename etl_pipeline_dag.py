from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.sensors.filesystem import FileSensor

# Default arguments for DAG
default_args = {
    'owner': 'kelompok3',
    'depends_on_past': False,
    'email': ['bigdata@itera.ac.id'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
dag = DAG(
    'ecommerce_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for e-commerce data',
    schedule_interval='0 */3 * * *',  # Every 3 hours
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['ecommerce', 'etl', 'hadoop', 'spark'],
)

# Task untuk memverifikasi ketersediaan data di bronze layer
check_bronze_data = FileSensor(
    task_id='check_bronze_data',
    filepath='/data/bronze/transactions/',  # Sesuaikan dengan path di HDFS
    poke_interval=60,  # Cek setiap 60 detik
    timeout=600,  # Timeout setelah 10 menit
    dag=dag,
)

# Task untuk memproses data dari bronze ke silver layer
bronze_to_silver = SparkSubmitOperator(
    task_id='bronze_to_silver',
    application='/opt/airflow/dags/scripts/etl/bronze_to_silver.py',
    conn_id='spark_default',
    verbose=True,
    conf={'spark.master': 'yarn',
          'spark.driver.memory': '4g',
          'spark.executor.memory': '4g',
          'spark.executor.cores': '2',
          'spark.executor.instances': '2'},
    dag=dag,
)

# Task untuk memverifikasi ketersediaan data di silver layer
check_silver_data = FileSensor(
    task_id='check_silver_data',
    filepath='/data/silver/transactions/',  # Sesuaikan dengan path di HDFS
    poke_interval=60,
    timeout=600,
    dag=dag,
)

# Task untuk memproses data dari silver ke gold layer
silver_to_gold = SparkSubmitOperator(
    task_id='silver_to_gold',
    application='/opt/airflow/dags/scripts/etl/silver_to_gold.py',
    conn_id='spark_default',
    verbose=True,
    conf={'spark.master': 'yarn',
          'spark.driver.memory': '4g',
          'spark.executor.memory': '4g',
          'spark.executor.cores': '2',
          'spark.executor.instances': '2'},
    dag=dag,
)

# Task untuk melakukan analisis segmentasi pelanggan
customer_segmentation = SparkSubmitOperator(
    task_id='customer_segmentation',
    application='/opt/airflow/dags/scripts/etl/customer_segmentation.py',
    conn_id='spark_default',
    verbose=True,
    conf={'spark.master': 'yarn',
          'spark.driver.memory': '4g',
          'spark.executor.memory': '4g',
          'spark.executor.cores': '2',
          'spark.executor.instances': '2'},
    dag=dag,
)

# Task untuk memverifikasi hasil analisis
validate_gold_data = BashOperator(
    task_id='validate_gold_data',
    bash_command='hdfs dfs -ls /data/gold/ | grep "customer_segments"',
    dag=dag,
)

# Task untuk membuat laporan hasil segmentasi
generate_report = BashOperator(
    task_id='generate_report',
    bash_command='python /opt/airflow/dags/scripts/generate_report.py',
    dag=dag,
)

# Definisikan alur task dalam DAG
check_bronze_data >> bronze_to_silver >> check_silver_data >> silver_to_gold >> customer_segmentation >> validate_gold_data >> generate_report