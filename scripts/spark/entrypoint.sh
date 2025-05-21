#!/bin/bash

# Start SSH service
sudo service ssh start

# Menentukan node type dari environment variable
NODE_TYPE=${NODE_TYPE:-worker}
SPARK_MASTER=${SPARK_MASTER:-spark://spark-master:7077}

case "$NODE_TYPE" in
  "master")
    echo "Starting as Spark Master..."
    # Start Spark Master
    $SPARK_HOME/sbin/start-master.sh
    
    # Keep container running
    tail -f $SPARK_HOME/logs/*
    ;;
    
  "worker")
    echo "Starting as Spark Worker..."
    # Wait for spark master
    until nc -z spark-master 7077; do
      echo "Waiting for Spark Master to be available..."
      sleep 2
    done
    
    # Start Spark Worker
    $SPARK_HOME/sbin/start-slave.sh $SPARK_MASTER
    
    # Keep container running
    tail -f $SPARK_HOME/logs/*
    ;;
    
  *)
    echo "Unknown node type: $NODE_TYPE"
    exit 1
    ;;
esac