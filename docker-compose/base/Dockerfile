FROM ubuntu:20.04

# Hindari prompt selama instalasi
ENV DEBIAN_FRONTEND=noninteractive

# Update repositori dan install dependensi
RUN apt-get update && apt-get install -y \
    openjdk-8-jdk \
    wget \
    curl \
    netcat \
    gnupg \
    net-tools \
    vim \
    apt-transport-https \
    software-properties-common \
    python3 \
    python3-pip \
    ssh \
    rsync \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java home
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Buat user hadoop
RUN useradd -m -s /bin/bash hadoop && \
    echo "hadoop:hadoop" | chpasswd && \
    adduser hadoop sudo

# Setup SSH tanpa password
RUN mkdir -p /home/hadoop/.ssh && \
    ssh-keygen -t rsa -P '' -f /home/hadoop/.ssh/id_rsa && \
    cat /home/hadoop/.ssh/id_rsa.pub >> /home/hadoop/.ssh/authorized_keys && \
    chmod 0600 /home/hadoop/.ssh/authorized_keys && \
    chown -R hadoop:hadoop /home/hadoop/.ssh

# Setup SSH service
RUN mkdir /var/run/sshd && \
    echo 'StrictHostKeyChecking no' >> /etc/ssh/ssh_config

# Set environment untuk Python
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.8/site-packages

# Install Python libraries
RUN pip3 install --upgrade pip && \
    pip3 install numpy pandas scipy scikit-learn matplotlib seaborn pyspark

WORKDIR /home/hadoop

USER hadoop

CMD ["/bin/bash"]