from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, sum as _sum, avg as _avg, max as _max, min as _min,
    countDistinct, when, datediff, to_date, current_date,
    split, regexp_replace, stddev, lit, row_number, date_format,
    month, year, dayofweek, round, desc, expr
)
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml import Pipeline

# ─────────────────────────────────────────────────────────────────────────────
# 1) KONFIGURASI & PATH
# ─────────────────────────────────────────────────────────────────────────────
silver_path = "hdfs://namenode:9000/data/silver"
gold_path   = "hdfs://namenode:9000/data/gold"
model_path  = "hdfs://namenode:9000/models"

spark = SparkSession.builder \
    .appName("EnhancedCustomerSegmentation") \
    .enableHiveSupport() \
    .config("spark.sql.warehouse.dir",    "hdfs://namenode:9000/user/hive/warehouse") \
    .config("spark.hadoop.hive.metastore.uris", "thrift://hive-server:10000") \
    .getOrCreate()


# ─────────────────────────────────────────────────────────────────────────────
# 2) LOAD & PREPARE DATA GOLD + SILVER
# ─────────────────────────────────────────────────────────────────────────────
def read_gold(table):
    print(f"▶ Loading GOLD: {table}")
    return spark.read.parquet(f"{gold_path}/{table}")

def read_silver(table):
    print(f"▶ Loading SILVER: {table}")
    return spark.read.parquet(f"{silver_path}/{table}")

def load_and_prepare_customer_data():
    # Gold tables
    customers_df    = read_gold("customer_metrics")
    transactions_df = read_gold("transaction_metrics")
    products_df     = read_gold("product_metrics")
    province_df     = read_gold("province_metrics")
    city_df         = read_gold("city_metrics")
    return customers_df, transactions_df, products_df, province_df, city_df


# ─────────────────────────────────────────────────────────────────────────────
# 3) FEATURE ENGINEERING KOMPREHENSIF
# ─────────────────────────────────────────────────────────────────────────────
def create_behavioral_features(customers, transactions, products, province, city):
    # Mulai dengan base customer metrics
    df = customers.withColumnRenamed("id_pelanggan", "customer_id")
    
    # --- Temporal / Behavioral dari transaction_metrics ---
    tx = transactions.withColumnRenamed("id_pelanggan", "customer_id")
    temp = tx.groupBy("customer_id").agg(
        _avg("total_transaksi").alias("avg_transaction_value"),
        _avg("jumlah_item_berbeda").alias("avg_items_per_tx"),
        _avg("harga_rata_rata_item").alias("avg_item_price"),
        _sum(when(col("bulan_transaksi").isin([12,1,2]),1).otherwise(0)).alias("winter_tx"),
        _sum(when(col("bulan_transaksi").isin([6,7,8]),1).otherwise(0)).alias("summer_tx"),
        _sum(when(col("hari_transaksi").isin([1,7]),1).otherwise(0)).alias("weekend_tx"),
        countDistinct("bulan_transaksi").alias("active_months"),
        countDistinct("tahun_transaksi").alias("active_years")
    )
    df = df.join(temp, on="customer_id", how="left")
    
    # --- Category features via SILVER data ---
    orders = read_silver("transactions").select("id_order", "id_pelanggan")
    items  = read_silver("order_items").select("id_order","id_produk","jumlah","harga")
    prods  = read_silver("products").select("id_produk","kategori_produk")
    
    cust_prod = orders.join(items, "id_order") \
        .join(prods, "id_produk") \
        .withColumnRenamed("id_pelanggan","customer_id")
    
    cat_feats = cust_prod.groupBy("customer_id").agg(
        countDistinct("kategori_produk").alias("category_diversity"),
        _max("harga").alias("max_product_price"),
        _min("harga").alias("min_product_price"),
        _avg("harga").alias("avg_product_price"),
        _sum("jumlah").alias("total_items_bought")
    )
    top_cat = cust_prod.groupBy("customer_id","kategori_produk") \
        .agg(_sum("jumlah").alias("qty")) \
        .withColumn("rank", row_number().over(
            Window.partitionBy("customer_id").orderBy(desc("qty")))) \
        .filter(col("rank")==1) \
        .select("customer_id", col("kategori_produk").alias("preferred_category"))
    
    df = df.join(cat_feats, "customer_id", "left") \
           .join(top_cat, "customer_id", "left")
    
    # --- Geographical features from province & city (GOLD) ---
    prov = province.select(
        col("provinsi_pelanggan").alias("province"),
        col("jumlah_pelanggan").alias("province_customer_count"),
        col("rata_rata_belanja_provinsi").alias("province_avg_spending")
    )
    city  = city.select(
        col("provinsi_pelanggan").alias("province"),
        col("kota_kabupaten_pelanggan").alias("city"),
        col("jumlah_pelanggan").alias("city_customer_count"),
        col("rata_rata_belanja_kota").alias("city_avg_spending")
    )
    df = df.join(prov, "province", "left") \
           .join(city, ["province","city"], "left") \
           .withColumn("is_major_city", when(col("city_customer_count")>=1000,1).otherwise(0))
    
    # --- RFM & Segmentation existing fields ---
    df = df.withColumn(
        "segment_score",
        when(col("segmen_pelanggan")=="Platinum",4)
         .when(col("segmen_pelanggan")=="Gold",3)
         .when(col("segmen_pelanggan")=="Silver",2)
         .otherwise(1)
    ).withColumn(
        "purchase_frequency_score",
        when(col("jumlah_transaksi")>=20,5)
         .when(col("jumlah_transaksi")>=10,4)
         .when(col("jumlah_transaksi")>=5,3)
         .otherwise(1)
    ).withColumn(
        "monetary_score",
        when(col("nilai_belanja")>=2000,5)
         .when(col("nilai_belanja")>=1000,4)
         .when(col("nilai_belanja")>=500,3)
         .otherwise(1)
    )
    # Recency
    if "last_purchase_date" in df.columns:
        df = df.withColumn("days_since_last", datediff(current_date(), col("last_purchase_date"))) \
               .withColumn("recency_score",
                   when(col("days_since_last")<=30,5)
                  .when(col("days_since_last")<=90,4)
                  .otherwise(1)
               )
    else:
        df = df.withColumn("recency_score", lit(3))
    
    # CLV & derived features
    df = df.withColumn(
        "customer_lifetime_value",
        col("nilai_belanja") * col("purchase_frequency_score") * col("recency_score") / 100
    ).withColumn(
        "avg_order_value", col("nilai_belanja")/col("jumlah_transaksi")
    ).withColumn(
        "product_diversity_ratio", col("jumlah_produk_berbeda")/col("jumlah_transaksi")
    )
    
    # Fill nulls
    for c in df.schema.fields:
        if c.dataType.simpleString() in ("int","double","long","float"):
            df = df.fillna({c.name: 0})
    for cat in ("preferred_category","segmen_pelanggan","province","city"):
        if cat in df.columns:
            df = df.fillna({cat: "Unknown"})
    
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4) PREPARE & SCALE FEATURES UNTUK K-MEANS
# ─────────────────────────────────────────────────────────────────────────────
def prepare_for_clustering(df):
    # select features
    baseline = [
        "jumlah_transaksi","nilai_belanja","rata_rata_belanja","jumlah_produk_berbeda",
        "segment_score","purchase_frequency_score","monetary_score"
    ]
    optional = [f for f in [
        "avg_transaction_value","avg_items_per_tx","avg_item_price",
        "winter_tx","summer_tx","weekend_tx","active_months","active_years",
        "category_diversity","total_items_bought","province_customer_count",
        "city_customer_count","is_major_city","recency_score"
    ] if f in df.columns]

    features = baseline + optional
    print("Features used:", features)
    
    assembler = VectorAssembler(inputCols=features, outputCol="features", handleInvalid="skip")
    scaler    = StandardScaler(inputCol="features",   outputCol="scaled_features", withMean=True, withStd=True)
    model     = Pipeline(stages=[assembler, scaler]).fit(df)
    prepared  = model.transform(df).filter(col("scaled_features").isNotNull())
    return prepared, model, features


# ─────────────────────────────────────────────────────────────────────────────
# 5) TEMUKAN k OPTIMAL & TRAIN KMEANS
# ─────────────────────────────────────────────────────────────────────────────
def find_optimal_k(data, max_k=7):
    evaluator = ClusteringEvaluator(featuresCol="scaled_features", predictionCol="prediction")
    scores = []
    for k in range(2, max_k+1):
        km = KMeans(k=k, seed=42, featuresCol="scaled_features")
        pred = km.fit(data).transform(data)
        sil = evaluator.evaluate(pred)
        # balance metric omitted for ringkas
        scores.append((k, sil))
        print(f"k={k}, silhouette={sil:.4f}")
    best = max(scores, key=lambda x: x[1])[0]
    print("Optimal k:", best)
    return best

def train_and_segment(data, k):
    model = KMeans(k=k, seed=42, featuresCol="scaled_features", predictionCol="cluster").fit(data)
    return model.transform(data), model

# ─────────────────────────────────────────────────────────────────────────────
# 6) SIMPAN HASIL & MODEL
# ─────────────────────────────────────────────────────────────────────────────
def save_results(segmented, cluster_model, prep_model, features):
    print("▶ Saving segmented data to GOLD/customer_segments_enhanced")
    segmented.select("customer_id","cluster",*features) \
        .write.mode("overwrite") \
        .parquet(f"{gold_path}/customer_segments_enhanced")

    # Daftarkan sebagai Hive table customer_segments_table
    spark.sql("CREATE DATABASE IF NOT EXISTS ecommerce_analytics")
    spark.sql(f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS ecommerce_analytics.customer_segments_table (
            customer_id STRING,
            cluster INT
            /* kolom lain bisa didefinisikan atau gunakan LIKE clause */
        )
        STORED AS PARQUET
        LOCATION '{gold_path}/customer_segments_enhanced'
    """)

    # Simpan model & pipeline
    cluster_model.write().overwrite().save(f"{model_path}/kmeans_customer_segmentation")
    prep_model.write().overwrite().save(f"{model_path}/preprocessing_pipeline")


# ─────────────────────────────────────────────────────────────────────────────
# 7) MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cust, tx, prod, prov, city = load_and_prepare_customer_data()
    enriched = create_behavioral_features(cust, tx, prod, prov, city)
    prepared, prep_model, feat_list = prepare_for_clustering(enriched)
    k_opt = find_optimal_k(prepared, max_k=7)
    segmented, kmodel = train_and_segment(prepared, k_opt)
    save_results(segmented, kmodel, prep_model, feat_list)
    print("✅ Enhanced segmentation pipeline completed.")
    spark.stop()
