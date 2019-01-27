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

# Access to google object storage via gsutil
RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

# Common Configuration
COPY src/entrypoint /entrypoint
COPY src/nginx.conf //etc/nginx/nginx.conf
COPY src/dhparam-2048.pem /etc/ssl/certs/dhparam-2048.pem
COPY src/proxy_params /etc/nginx/proxy_params
COPY src/cors_wide_open /etc/nginx/cors_wide_open

# Permissions, paths, ports, entrypoint
RUN chmod a+x /entrypoint

CMD ["/entrypoint"]
