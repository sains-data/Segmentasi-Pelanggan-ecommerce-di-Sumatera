#!/bin/bash

# Start SSH service
sudo service ssh start

# Menentukan node type dari environment variable
NODE_TYPE=${NODE_TYPE:-server}

# Wait for MySQL
until nc -z hive-metastore-db 3306; do
  echo "Waiting for MySQL to be available..."
  sleep 2
done

# Wait for namenode
until nc -z namenode 9000; do
  echo "Waiting for namenode to be available..."
  sleep 2
done

# Initialize schema if needed
if [ "$NODE_TYPE" = "server" ]; then
  echo "Initializing Hive Metastore schema..."
  $HIVE_HOME/bin/schematool -dbType mysql -initSchema
  
  echo "Starting HiveServer2..."
  $HIVE_HOME/bin/hiveserver2 --hiveconf hive.server2.enable.doAs=false &
  
  # Keep container running
  tail -f $HIVE_HOME/logs/*
else
  echo "Unknown node type: $NODE_TYPE"
  exit 1
fi