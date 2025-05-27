from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_eng',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'bronze_silver_gold_viz',
    default_args=default_args,
    start_date=datetime(2025,5,1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    # 1) Ingest raw ke Bronze
    t1 = BashOperator(
        task_id='mysql_to_hdfs',
        application='/opt/src/ingestion/mysql_to_hdfs.py',
        conn_id='yarn_default'
    )

    # 2) Clean ke Silver
    t2 = SparkSubmitOperator(
        task_id='clean_silver',
        application='/opt/src/processing/bronze_to_silver.py',
        conn_id='yarn_default'
    )

    # 3) Segmentasi → Gold
    t3 = SparkSubmitOperator(
        task_id='gold_segmentation',
        application='/opt/src/analytics/segmentation.py',
        conn_id='yarn_default'
    )

    # 4) (Optional) Refresh data source di Superset lewat REST API
    refresh = SimpleHttpOperator(
        task_id='refresh_superset',
        http_conn_id='superset_api',          # koneksi di Airflow UI
        method='POST',
        endpoint='/api/v1/dashboard/refresh',
        data={"dashboard_id": 42},            # ganti sesuai ID Dashboard
        headers={"Content-Type": "application/json"}
    )

    t1 >> t2 >> t3 >> refresh
