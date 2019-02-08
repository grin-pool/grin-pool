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
      vim

# Common Configuration
COPY src/entrypoint /entrypoint
COPY src/nginx.conf /etc/nginx/nginx.conf
COPY src/dhparam-2048.pem /etc/ssl/certs/dhparam-2048.pem
COPY src/proxy_params /etc/nginx/proxy_params
COPY src/cors_wide_open /etc/nginx/cors_wide_open

# Permissions, paths, ports, entrypoint
RUN chmod a+x /entrypoint

CMD ["/entrypoint"]

EXPOSE 80
EXPOSE 443
EXPOSE 3332
EXPOSE 3333
EXPOSE 3334
EXPOSE 13416
EXPOSE 23416

# General
COPY src/nginx.conf /etc/nginx/nginx.conf

# Proxy Config
COPY src/stratum_proxy_params  /etc/nginx/stratum_proxy_params

# Cloudflare CA
COPY src/cloudflare_origin_rsa.pem /etc/ssl/certs/cloudflare_origin_rsa.pem
COPY src/cloudflare_origin_ecc.pem /etc/ssl/certs/cloudflare_origin_ecc.pem
RUN cd /etc/ssl/certs/ && \
    ln -s cloudflare_origin_rsa.pem d947dbd7.0 && \
    ln -s cloudflare_origin_rsa.pem d947dbd7 && \
    ln -s cloudflare_origin_ecc.pem 6976c116.0 && \
    ln -s cloudflare_origin_ecc.pem 6976c116

RUN update-ca-certificates --fresh


# pool.bitgrin.io
RUN mkdir -p /pool.bitgrin.io/
COPY src/bitgrinpool.stream.conf /pool.bitgrin.io/bitgrinpool.stream.conf
COPY src/bitgrinpool.http.conf /pool.bitgrin.io/bitgrinpool.http.conf
