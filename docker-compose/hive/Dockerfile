FROM hadoop-ecommerce-base:latest

# Version
ENV HIVE_VERSION=4.0.1

# Download dan install Hive
RUN wget https://downloads.apache.org/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz && \
    tar -xzf apache-hive-${HIVE_VERSION}-bin.tar.gz -C /home/hadoop && \
    rm apache-hive-${HIVE_VERSION}-bin.tar.gz && \
    ln -s /home/hadoop/apache-hive-${HIVE_VERSION}-bin /home/hadoop/hive

# Download MySQL JDBC Driver
RUN wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.0.32.tar.gz && \
    tar -xzf mysql-connector-j-8.0.32.tar.gz && \
    cp mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar /home/hadoop/hive/lib/ && \
    rm -rf mysql-connector-j-8.0.32 mysql-connector-j-8.0.32.tar.gz

# Set environment variables
ENV HIVE_HOME=/home/hadoop/hive
ENV PATH=$PATH:${HIVE_HOME}/bin
ENV CLASSPATH=$CLASSPATH:${HIVE_HOME}/lib/*

# Setup Hive environment
COPY config/hive/hive-site.xml ${HIVE_HOME}/conf/

# Copy startup scripts
COPY scripts/hive/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]