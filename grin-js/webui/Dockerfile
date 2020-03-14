FROM node:latest
WORKDIR /webui
COPY package.json /webui/
RUN yarn

RUN set -ex && \
    apt-get update && \
    apt-get --no-install-recommends --yes install \
      vim \
      net-tools \
      procps

EXPOSE 3005
EXPOSE 5000

COPY . /webui
RUN yarn build
RUN yarn global add serve
COPY entrypoint.sh /

CMD ["/entrypoint.sh"]
