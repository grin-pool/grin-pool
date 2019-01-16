FROM splunk/universalforwarder:latest

USER root

ENV SPLUNK_START_ARGS=--accept-license

EXPOSE 9997

COPY run.sh /

ENTRYPOINT ["/run.sh"]
