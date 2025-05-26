#!/bin/bash

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


## Setup ENV variables

export JAVA_HOME="/usr/lib/jvm/java-1.8.0"
export HDFS_NAMENODE_USER="root"
export HDFS_SECONDARYNAMENODE_USER="root"
export HDFS_DATANODE_USER="root"
export YARN_RESOURCEMANAGER_USER="root"
export YARN_NODEMANAGER_USER="root"

export HADOOP_HOME="/hadoop"
export HADOOP_ROOT_LOGGER=DEBUG
export HADOOP_COMMON_LIB_NATIVE_DIR="/hadoop/lib/native"
export HADOOP_CLASSPATH=$HADOOP_CLASSPATH

# Step 7: Tez configs
export TEZ_HOME="/tez"
export HADOOP_CLASSPATH=$TEZ_HOME/*:$TEZ_HOME/lib/*:$HADOOP_CLASSPATH
export TEZ_CONF_DIR=/hive/conf/

# step 8: Hive configs
export HIVE_HOME="/hive"
export PATH=$PATH:$HIVE_HOME/bin

# step 9: Hbase configs
export HBASE_HOME="/hbase"
export PATH=$PATH:$HBASE_HOME/bin

# Step 10: Spark configs
export SPARK_HOME="/spark/"
export PATH=$PATH:$SPARK_HOME/bin

## Add it to bashrc for starting hadoop
echo 'export JAVA_HOME="/usr/lib/jvm/java-1.8.0"' >> ~/.bashrc
echo 'export HADOOP_HOME="/hadoop"' >> ~/.bashrc
echo 'export HADOOP_CLASSPATH="$HADOOP_CLASSPATH"' >> ~/.bashrc
echo 'export PATH=$PATH:/hadoop/bin' >> ~/.bashrc
echo 'export TEZ_HOME="/tez"' >> ~/.bashrc
echo 'export HADOOP_CLASSPATH="$TEZ_HOME/*:$TEZ_HOME/lib/*:$HADOOP_CLASSPATH"' >> ~/.bashrc
echo 'export TEZ_CONF_DIR="/hive/conf/"' >> ~/.bashrc
echo 'export HIVE_HOME="/hive"' >> ~/.bashrc
echo 'export PATH=$PATH:$HIVE_HOME/bin' >> ~/.bashrc
echo 'export HBASE_HOME="/hbase"' >> ~/.bashrc
echo 'export PATH=$PATH:$HBASE_HOME/bin' >> ~/.bashrc
echo 'export SPARK_HOME="/spark/"' >> ~/.bashrc
echo 'export PATH=$PATH:$SPARK_HOME/bin' >> ~/.bashrc

rm /hadoop
ln -sf /hadoop-3.4.1 /hadoop
ln -sf /apache-hive-4.0.1-bin /hive
ln -sf /apache-tez-0.10.4-bin /tez
ln -sf /hbase-2.5.11 /hbase
ln -sf /apache-zookeeper-3.8.4-bin /zookeeper
ln -sf /spark-3.5.5-bin-hadoop3 /spark

# Copy the config files
cp /conf/core-site.xml /hadoop/etc/hadoop
cp /conf/hdfs-site.xml /hadoop/etc/hadoop
cp /conf/hadoop-env.sh /hadoop/etc/hadoop
cp /conf/hive-site.xml /hive/conf/
cp /conf/hbase-site.xml /hbase/conf/
cp /conf/hbase-env.sh /hbase/conf/


cp /mysql-connector-java-8.0.28.jar /hive/lib

gprn "set up mysql"
sudo service mysql start

# Set root password
mysql -uroot -e "set password = PASSWORD('root');"
mysql -uroot -e "grant all privileges on *.* to 'root'@'localhost' identified by 'root';"
mysql -uroot -e "CREATE USER 'hive'@'localhost' IDENTIFIED BY 'hive';"
mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'hive'@'localhost';"
mysql -uroot -e "CREATE USER 'hive'@'%' IDENTIFIED BY 'hive';"
mysql -uroot -e "GRANT ALL PRIVILEGES ON *.* TO 'hive'@'%';"
mysql -uroot -e "FLUSH PRIVILEGES;"

service ssh start

gprn "start yarn"
hadoop/sbin/start-yarn.sh &
sleep 5

gprn "Formatting name node"
hadoop/bin/hdfs namenode -format

gprn "Start hdfs"
hadoop/sbin/start-dfs.sh

jps

# Initialize Zookeeper
gprn "Setting up Zookeeper..."
echo "1" > $ZOOKEEPER_HOME/data/myid
$ZOOKEEPER_HOME/bin/zkServer.sh start

# Wait for Zookeeper to start
sleep 10

gprn "Start HBase"
hbase/bin/start-hbase.sh

gprn "Set up metastore DB"
hive/bin/schematool -userName hive -passWord 'hive' -dbType mysql -initSchema

gprn "Start HMS server"
hive/bin/hive --service metastore -p 10000 &

gprn "Sleep and wait for HMS to be up and running"
sleep 20

gprn "Start HiveServer2"
#hive/bin/hive --service hiveserver2 --hiveconf hive.server2.thrift.port=10001 --hiveconf hive.execution.engine=mr
hive/bin/hive --service hiveserver2 --hiveconf hive.server2.thrift.port=10001 --hiveconf hive.execution.engine=tez

sleep 20000