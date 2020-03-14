FROM nginx:1.15.8
  
RUN set -ex && \
    apt-get update && \
    apt-get -q --no-install-recommends --yes install \
      software-properties-common \
      python3 \
      python3-pip \
      gpg \
      git \
      dirmngr \
      curl \
      ruby \
      procps \
      net-tools \
      htop \
      vim \
      locales

RUN set -ex && \
    echo "deb http://ftp.debian.org/debian stretch-backports main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get -q --no-install-recommends --yes install \
      python-certbot-nginx
                  

# Common Configuration
COPY src/entrypoint.sh /entrypoint.sh
COPY src/renew_certs.sh /renew_certs.sh
COPY src/nginx.conf /etc/nginx/nginx.conf
COPY src/dhparam-2048.pem /etc/ssl/certs/dhparam-2048.pem
COPY src/proxy_params /etc/nginx/proxy_params
COPY src/cors_wide_open /etc/nginx/cors_wide_open

# Permissions, paths, ports, entrypoint
RUN chmod a+x /entrypoint.sh

CMD ["/entrypoint"]

EXPOSE 80
EXPOSE 443
EXPOSE 3333

# General
COPY src/nginx.conf /etc/nginx/nginx.conf

# Proxy Config
COPY src/stratum_proxy_params  /etc/nginx/stratum_proxy_params

# Automatic Renew
COPY src/renew_certs.sh /

RUN update-ca-certificates --fresh

# mwfloopool
RUN mkdir -p /mwfloopool.com/
COPY src/mwfloopool.stream.conf /mwfloopool.com/mwfloopool.stream.conf
COPY src/mwfloopool.http.conf /mwfloopool.com/mwfloopool.http.conf
