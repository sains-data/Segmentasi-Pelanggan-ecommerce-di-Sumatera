# The maximum amount of heap to use, in MB. Default is 1000.
export HADOOP_HEAPSIZE=1024
export JAVA_HOME="/usr/lib/jvm/java-1.8.0"
export HADOOP_NAMENODE_OPTS="$HADOOP_NAMENODE_OPTS -Xmx512m"
export YARN_OPTS="$YARN_OPTS -Xmx256m"