#!/bin/bash

# Start SSH service
sudo service ssh start

# Menentukan node type dari environment variable
NODE_TYPE=${NODE_TYPE:-datanode}

case "$NODE_TYPE" in
  "namenode")
    echo "Starting as NameNode..."
    # Format namenode jika belum diformat
    if [ ! -d "/data/namenode" ]; then
      echo "Formatting namenode directory..."
      $HADOOP_HOME/bin/hdfs namenode -format
    fi
    
    # Start NameNode
    $HADOOP_HOME/bin/hdfs --daemon start namenode
    
    # Keep container running
    tail -f $HADOOP_HOME/logs/*
    ;;
    
  "resourcemanager")
    echo "Starting as ResourceManager..."
    # Start ResourceManager
    $HADOOP_HOME/bin/yarn --daemon start resourcemanager
    
    # Start HistoryServer
    $HADOOP_HOME/bin/mapred --daemon start historyserver
    
    # Keep container running
    tail -f $HADOOP_HOME/logs/*
    ;;
    
  "datanode")
    echo "Starting as DataNode..."
    # Wait for namenode
    until nc -z namenode 9000; do
      echo "Waiting for namenode to be available..."
      sleep 2
    done
    
    # Start DataNode
    $HADOOP_HOME/bin/hdfs --daemon start datanode
    
    # Start NodeManager
    $HADOOP_HOME/bin/yarn --daemon start nodemanager
    
    # Keep container running
    tail -f $HADOOP_HOME/logs/*
    ;;
    
  *)
    echo "Unknown node type: $NODE_TYPE"
    exit 1
    ;;
esac