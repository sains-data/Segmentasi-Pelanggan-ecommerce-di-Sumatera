#!/bin/bash
set -e

# warna
eg='\033[0;32m'
enc='\033[0m'
echoe () {
    OIFS=${IFS}
    IFS='%'
    echo -e $@
    IFS=${OIFS}
}
gprn() {
    echoe "${eg} >> ${1}${enc}"
}

# ------------------------------------------------------------------
# 1) ENVIRONMENT VARIABLES (runtime)
# ------------------------------------------------------------------
export JAVA_HOME="/usr/lib/jvm/java-1.8.0"
export HADOOP_HOME="/hadoop"
export HIVE_HOME="/hive"
export SQOOP_HOME="/sqoop"
export SPARK_HOME="/spark"
export ZOOKEEPER_HOME="/zookeeper"
export AIRFLOW_HOME="/airflow"

export TEZ_HOME="/tez"
export HADOOP_CLASSPATH=$TEZ_HOME/*:$TEZ_HOME/lib/*:$HADOOP_CLASSPATH
export TEZ_CONF_DIR=/hive/conf/

export HDFS_NAMENODE_USER="root"
export HDFS_SECONDARYNAMENODE_USER="root"
export HDFS_DATANODE_USER="root"
export YARN_RESOURCEMANAGER_USER="root"
export YARN_NODEMANAGER_USER="root"

export HADOOP_ROOT_LOGGER=DEBUG
export HADOOP_COMMON_LIB_NATIVE_DIR="$HADOOP_HOME/lib/native"

export PATH=$PATH:$HADOOP_HOME/bin:$HIVE_HOME/bin:$SQOOP_HOME/bin:$SPARK_HOME/bin

# ------------------------------------------------------------------
# 2) Tambahkan ENV ke .bashrc (jika login shell interaktif)
# ------------------------------------------------------------------
cat << 'EOF' >> ~/.bashrc
export JAVA_HOME="/usr/lib/jvm/java-1.8.0"
export HADOOP_HOME="/hadoop"
export HIVE_HOME="/hive"
export SQOOP_HOME="/sqoop"
export SPARK_HOME="/spark"
export TEZ_HOME="/tez"
export HADOOP_CLASSPATH="$TEZ_HOME/*:$TEZ_HOME/lib/*:$HADOOP_CLASSPATH"
export TEZ_CONF_DIR="/hive/conf/"
export ZOOKEEPER_HOME="/zookeeper"
export AIRFLOW_HOME="/airflow"
export PATH=$PATH:$HADOOP_HOME/bin:$HIVE_HOME/bin:$SQOOP_HOME/bin:$SPARK_HOME/bin
EOF

# ------------------------------------------------------------------
# 3) Pastikan symbolic links ke versi yang benar
# ------------------------------------------------------------------
rm -f /hadoop && ln -s /hadoop-3.4.1 /hadoop
rm -f /hive   && ln -s /apache-hive-4.0.1-bin /hive
rm -f /spark  && ln -s /spark-3.5.5-bin-hadoop3 /spark
rm -f /zookeeper && ln -s /apache-zookeeper-3.8.4-bin /zookeeper
rm -f /sqoop  && ln -s /sqoop-1.4.7.bin__hadoop260 /sqoop
rm -f /tez && ln -s /apache-tez-0.10.4-bin /tez

# ------------------------------------------------------------------
# 4) Copy konfigurasi Hadoop & Hive
# ------------------------------------------------------------------
gprn "Copy Hadoop & Hive configs"
cp /conf/core-site.xml      $HADOOP_HOME/etc/hadoop/
cp /conf/hdfs-site.xml      $HADOOP_HOME/etc/hadoop/
cp /conf/hadoop-env.sh      $HADOOP_HOME/etc/hadoop/
cp /conf/hive-site.xml      $HIVE_HOME/conf/

# Pastikan JDBC driver ada untuk Hive & Sqoop
gprn "Copy MySQL connector"
cp /mysql-connector-java-8.0.28.jar $HIVE_HOME/lib/
cp /mysql-connector-java-8.0.28.jar $SQOOP_HOME/lib/

# ------------------------------------------------------------------
# 5) Start MySQL & Setup users
# ------------------------------------------------------------------
gprn "Setup MySQL"
service mysql start

mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';"
mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost';"
mysql -uroot -proot -e "CREATE USER IF NOT EXISTS 'hive'@'localhost' IDENTIFIED BY 'hive';"
mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'hive'@'localhost';"
mysql -uroot -proot -e "FLUSH PRIVILEGES;"

# ------------------------------------------------------------------
# 6) Start SSH (untuk Hadoop & Spark)
# ------------------------------------------------------------------
gprn "Start SSH"
service ssh start

# ------------------------------------------------------------------
# 7) Format & Start HDFS + YARN
# ------------------------------------------------------------------
gprn "Formatting NameNode (jika pertama kali)"
$HADOOP_HOME/bin/hdfs namenode -format -force

gprn "Start HDFS"
$HADOOP_HOME/sbin/start-dfs.sh

gprn "Start YARN"
$HADOOP_HOME/sbin/start-yarn.sh

sleep 5
jps

# ------------------------------------------------------------------
# 8) Start Zookeeper
# ------------------------------------------------------------------
gprn "Start Zookeeper"
mkdir -p $ZOOKEEPER_HOME/data
echo "1" > $ZOOKEEPER_HOME/data/myid
$ZOOKEEPER_HOME/bin/zkServer.sh start

sleep 5

# ------------------------------------------------------------------
# 9) Initialize Hive metastore & Start Hive services
# ------------------------------------------------------------------
gprn "Init Hive metastore schema"
$HIVE_HOME/bin/schematool -dbType mysql -initSchema -userName hive -passWord hive

gprn "Start Hive Metastore"
nohup $HIVE_HOME/bin/hive --service metastore > /airflow/logs/hivemetastore.log 2>&1 &

sleep 5

gprn "Start HiveServer2 (Tez engine)"
nohup $HIVE_HOME/bin/hive --service hiveserver2 \
    --hiveconf hive.server2.thrift.port=10001 \
    --hiveconf hive.execution.engine=tez \
    > /airflow/logs/hiveserver2.log 2>&1 &

# ------------------------------------------------------------------
# 10) Start Spark History Server (opsional)
# ------------------------------------------------------------------
gprn "Start Spark History Server"
$SPARK_HOME/sbin/start-history-server.sh

# ------------------------------------------------------------------
# 11) Initialize & Start Airflow
# ------------------------------------------------------------------
gprn "Initialize Airflow DB"
airflow db init

gprn "Create Airflow admin user"
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email dbamizankhr@gmail.com \
    --password admin

gprn "Start Airflow Scheduler"
nohup airflow scheduler > /airflow/logs/scheduler.log 2>&1 &

gprn "Start Airflow Webserver (port 8080)"
nohup airflow webserver --port 8080 > /airflow/logs/webserver.log 2>&1 &

# ------------------------------------------------------------------
# 12) (Opsional) Start Sqoop (tidak ada daemon, siap dipakai cli)
# ------------------------------------------------------------------
gprn "Sqoop siap digunakan via CLI: \$SQOOP_HOME/bin/sqoop"

# ------------------------------------------------------------------
# 13) Keep container running
# ------------------------------------------------------------------
tail -f /dev/null
