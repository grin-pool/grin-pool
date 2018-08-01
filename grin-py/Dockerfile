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
        mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt && \
    sed -i '157 s/^##*//' /etc/locale.gen && \
    locale-gen

RUN pip3 install wheel && \
    pip3 install python-dateutil && \
    pip3 install pytz && \
    pip3 install requests && \
    pip3 install mysql-connector && \
    pip3 install configparser && \
    pip3 install sqlalchemy && \
    pip3 install pymysql && \
    pip3 install Flask && \
    pip3 install flask-restful

RUN cd /usr/bin && ln -s python3 python

ENV PATH=/usr/local/bin:$PATH
ENV PYTHONPATH=/usr/local/bin
WORKDIR /services

COPY grinbase/ /usr/local/bin/grinbase/
COPY grinlib/ /usr/local/bin/grinlib/
COPY services/*.py /usr/local/bin/
COPY api/ /usr/local/bin/api/

CMD ["/bin/sh"]
