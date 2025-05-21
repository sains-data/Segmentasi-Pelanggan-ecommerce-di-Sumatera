FROM hadoop-ecommerce-base:latest

# Version
ENV AIRFLOW_VERSION=2.6.0

# Install Airflow dan dependensi
RUN pip3 install apache-airflow==${AIRFLOW_VERSION} \
    apache-airflow-providers-apache-spark \
    apache-airflow-providers-apache-hdfs \
    apache-airflow-providers-apache-hive \
    apache-airflow-providers-http

# Setup Airflow home
ENV AIRFLOW_HOME=/home/hadoop/airflow

# Inisialisasi database Airflow
RUN airflow db init

# Buat user admin untuk Airflow
RUN airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Copy konfigurasi Airflow
COPY config/airflow/airflow.cfg ${AIRFLOW_HOME}/

# Copy DAGs
COPY dags/ ${AIRFLOW_HOME}/dags/

# Copy startup scripts
COPY scripts/airflow/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]