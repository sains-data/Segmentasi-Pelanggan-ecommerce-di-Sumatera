#!/bin/bash
docker run --rm -t --name bigdata-spark --hostname localhost -P -p 9866:9866 -p 9870:9870 -p 8088:8088 -p 9000:9000 -p 8000:8000 -p 10000:10000 -p 10001:10001 -p 10002:10002 -p 50030:50030 -p 2181:2181 -p 2888:2888 -p 3888:3888 -p 16000:16000 -p 16010:16010 -p 16020:16020 -p 16030:16030 -p 3306:3306 -p 4040:4040 -it -d bigdata-spark /bin/bash -c "/bootstrap.sh >/tmp/bootstrap.log"
