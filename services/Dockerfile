FROM grinpool/grin:latest

RUN set -ex && \
    apt-get update && \
    apt-get -q --no-install-recommends --yes install \
        locales \
        ca-certificates \
        curl \
        software-properties-common \
        build-essential \
        python \
        python-pip \
        python-setuptools \
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
        mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt && \
    sed -i '157 s/^##*//' /etc/locale.gen && \
    locale-gen

RUN pip install wheel && \
    pip install python-dateutil && \
    pip install pytz && \
    pip install requests && \
    pip install mysql-connector && \
    pip install configparser

ENV PATH=/usr/local/bin:$PATH
WORKDIR /services

COPY . /usr/local/bin/

