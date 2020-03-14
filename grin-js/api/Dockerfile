FROM node:latest

WORKDIR /api

RUN set -ex && \
    apt-get update && \
    apt-get --no-install-recommends --yes install \
    build-essential \
    libssl-dev \
    vim \
    net-tools \
    psmisc \
    htop \
    curl \
    telnet \
    python3-pip \
    libssl-dev 

COPY py/. /py/
RUN pip3 install -r /py/requirements.txt

COPY code/. /api/
RUN yarn global add forever && \
    yarn
ENV NODE_ENV=production

COPY entrypoint.sh /

CMD ["/entrypoint.sh"]
