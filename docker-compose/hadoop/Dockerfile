FROM hadoop-ecommerce-base:latest

# Version
ENV HADOOP_VERSION=3.4.1

# Download dan install Hadoop
RUN wget https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /home/hadoop && \
    rm hadoop-${HADOOP_VERSION}.tar.gz && \
    ln -s /home/hadoop/hadoop-${HADOOP_VERSION} /home/hadoop/hadoop

# Set environment variables
ENV HADOOP_HOME=/home/hadoop/hadoop
ENV HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
ENV PATH=$PATH:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin

# Setup Hadoop environment
COPY config/hadoop/*.xml ${HADOOP_CONF_DIR}/

# Copy startup scripts
COPY scripts/hadoop/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]