#!/bin/bash

# Start SSH service
sudo service ssh start

echo "Starting NiFi server..."
$NIFI_HOME/bin/nifi.sh start

# Wait for NiFi to start
$NIFI_HOME/bin/nifi.sh status

# Keep container running
tail -f $NIFI_HOME/logs/*.log