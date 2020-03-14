FROM docker.elastic.co/logstash/logstash:6.4.1

COPY run.sh /

WORKDIR /usr/share/logstash/config/
COPY logstash.yml /usr/share/logstash/config/
COPY jvm.options /usr/share/logstash/config/
COPY sharefilter.conf /usr/share/logstash/config/
COPY poolblockfilter.conf /usr/share/logstash/config/

ENTRYPOINT []
