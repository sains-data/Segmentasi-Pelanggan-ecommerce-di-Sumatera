FROM hadoop-ecommerce-base:latest

# Version
ENV SPARK_VERSION=3.5.5
ENV HADOOP_VERSION=3.4

# Download dan install Spark
RUN wget https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz -C /home/hadoop && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    ln -s /home/hadoop/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /home/hadoop/spark

# Set environment variables
ENV SPARK_HOME=/home/hadoop/spark
ENV PATH=$PATH:${SPARK_HOME}/bin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9-src.zip:$PYTHONPATH

# Setup Spark environment
COPY config/spark/*.conf ${SPARK_HOME}/conf/

# Copy startup scripts
COPY scripts/spark/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]