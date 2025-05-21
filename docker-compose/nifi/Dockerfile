FROM hadoop-ecommerce-base:latest

# Version
ENV NIFI_VERSION=2.4.0

# Download dan install NiFi
RUN wget https://downloads.apache.org/nifi/${NIFI_VERSION}/nifi-${NIFI_VERSION}-bin.zip && \
    sudo apt-get update && sudo apt-get install -y unzip && \
    unzip nifi-${NIFI_VERSION}-bin.zip -d /home/hadoop && \
    rm nifi-${NIFI_VERSION}-bin.zip && \
    ln -s /home/hadoop/nifi-${NIFI_VERSION} /home/hadoop/nifi

# Set environment variables
ENV NIFI_HOME=/home/hadoop/nifi
ENV PATH=$PATH:${NIFI_HOME}/bin

# Setup NiFi environment
COPY config/nifi/nifi.properties ${NIFI_HOME}/conf/

# Copy startup scripts
COPY scripts/nifi/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]