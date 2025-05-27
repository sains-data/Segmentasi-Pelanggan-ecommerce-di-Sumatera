# src/ingestion/mysql_to_hdfs.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import yaml

def create_spark_session():
    """Create Spark session with MySQL connector"""
    return SparkSession.builder \
        .appName("ECommerce-Data-Ingestion") \
        .config("spark.jars", "sains-data/Segmentasi-Pelanggan-ecommerce-di-Sumatera/mysql-connector-java-8.0.28.jar") \
        .getOrCreate()

def ingest_table_to_bronze(spark, table_name, mysql_config, hdfs_path):
    """Ingest data from MySQL to HDFS Bronze layer"""
    
    df = spark.read \
        .format("jdbc") \
        .option("url", f"jdbc:mysql://{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}") \
        .option("dbtable", table_name) \
        .option("user", mysql_config['username']) \
        .option("password", mysql_config['password']) \
        .option("driver", "com.mysql.cj.jdbc.Driver") \
        .load()
    
    # Add ingestion metadata
    df_with_metadata = df.withColumn("ingestion_date", current_timestamp()) \
                        .withColumn("source_system", lit("mysql_xampp"))
    
    # Write to HDFS as Parquet
    df_with_metadata.write \
        .mode("overwrite") \
        .option("path", f"{hdfs_path}/bronze/{table_name}") \
        .saveAsTable(f"bronze.{table_name}")
    
    print(f"Ingested {df.count()} records from {table_name} to Bronze layer")

def main():
    spark = create_spark_session()
    
    # Load configuration
    with open('/config/database.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    tables = ['customers', 'products', 'order_items', 'sellers', 'reviews', 'transactions']
    hdfs_base_path = "/data/bronze"
    
    for table in tables:
        ingest_table_to_bronze(spark, table, config['mysql'], hdfs_base_path)
    
    spark.stop()

if __name__ == "__main__":
    main()