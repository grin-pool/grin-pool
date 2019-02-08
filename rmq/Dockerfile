FROM rabbitmq

RUN set -ex && \
    apt-get update && \
    apt-get --no-install-recommends --yes install \
        python

#ENV RABBITMQ_USER mwgrinpool
#ENV RABBITMQ_PASSWORD rpassword

COPY rabbitmqadmin /
COPY definitions.json /
COPY import_config.sh /
COPY entrypoint.sh /

RUN rabbitmq-plugins enable rabbitmq_management
