FROM xxx/mwnginx-dockerbase

WORKDIR /keybase
RUN chown 1000:1000 /keybase
ENV HOME /keybase

EXPOSE 16423
EXPOSE 16723

RUN echo "keybase:x:1000:1000:,,,:/keybase:/bin/bash" >> /etc/passwd && \
    echo "keybase:x:1000:" >> /etc/group && \
    echo "keybase:x:17888:0:99999:7:::" >> /etc/shadow

COPY keybase_amd64.deb /keybase/
RUN set -ex && \
    apt-get update && \
    dpkg -i keybase_amd64.deb || /bin/true
RUN apt-get install -f --yes
RUN set -ex && \
    apt-get --no-install-recommends --yes install \
      vim \
      net-tools \
      procps

COPY entrypoint.sh /

CMD ["/entrypoint.sh"]
