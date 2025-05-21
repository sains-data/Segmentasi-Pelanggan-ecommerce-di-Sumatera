#!/bin/bash

# Wait for database to be ready
sleep 10

# Determine component to start
COMPONENT=${AIRFLOW_COMPONENT:-webserver}

case "$COMPONENT" in
  "webserver")
    echo "Starting Airflow webserver..."
    airflow webserver
    ;;
    
  "scheduler")
    echo "Starting Airflow scheduler..."
    airflow scheduler
    ;;
    
  *)
    echo "Unknown component: $COMPONENT"
    exit 1
    ;;
esac