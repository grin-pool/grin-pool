FROM grinpool/grin:latest

RUN set -ex && \
    apt-get update && \
    apt-get -q --no-install-recommends --yes install \
        locales \
        ca-certificates \
        curl \
	telnet \
        software-properties-common \
        build-essential \
        python3 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        g++ \
        git \
        cmake \
        libtool \
        autotools-dev \
        automake \
        pkg-config \
        libssl-dev \
        libevent-dev \
        bsdmainutils \
        net-tools \
        vim \
        psmisc \
        mysql-client \
        libpango1.0-0 \
        libpq-dev \
        libcairo2 \
        libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt && \
    sed -i '157 s/^##*//' /etc/locale.gen && \
    locale-gen

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

RUN cd /usr/bin && ln -s python3 python

ENV PATH=/usr/local/bin:$PATH
ENV PYTHONPATH=/usr/local/bin
WORKDIR /services

CMD touch XXX
COPY grinbase/ /usr/local/bin/grinbase/
COPY grinlib/ /usr/local/bin/grinlib/
COPY services/*.py /usr/local/bin/
COPY services/config.ini /usr/local/bin/
COPY api/ /usr/local/bin/api/
COPY webui/ /usr/local/bin/webui

CMD ["/bin/sh"]

#RUN set -ex && \
#    apt-get update && \
#    apt-get -q --no-install-recommends --yes install \
#        logrotate
#COPY utils/logrotate.conf /etc/
