FROM docker.elastic.co/logstash/logstash:6.4.1

COPY run.sh /

WORKDIR /usr/share/logstash/config/
COPY logstash.yml /usr/share/logstash/config/
COPY jvm.options /usr/share/logstash/config/
COPY poolsharefilter.conf /usr/share/logstash/config/
COPY grinsharefilter.conf /usr/share/logstash/config/

ENTRYPOINT []
