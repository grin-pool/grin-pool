FROM google/cloud-sdk:latest

RUN set -ex && \
    apt-get update && \
    apt-get -q --no-install-recommends --yes install \
      software-properties-common \
      locales \
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

# Vim Settings
RUN echo "set mouse=v" >> /root/.vimrc

# For Ruby route53 hook to parse a string
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# LetsEncrypt CertBot
RUN echo "deb http://deb.debian.org/debian stretch-backports main" >> /etc/apt/sources.list && \
    # add-apt-repository ppa:certbot/certbot && \
    set -ex && \
    apt-get update && \
    apt-get -q --no-install-recommends --yes install -t stretch-backports \
      certbot python-certbot-nginx

# dehydrated 
WORKDIR /etc/letsencrypt
RUN git clone https://github.com/lukas2511/dehydrated.git && \
    cd dehydrated && \
    ./dehydrated --register --accept-terms

# AWS SDK in ruby for dehydrated dns challenge route53 automation
RUN gem install aws-sdk && \
    gem install pry && \
    gem install awesome_print && \
    gem install public_suffix
# LetsEncrypt DNS challenge automation
COPY route53_hook.rb /usr/share/nginx/dehydrated/hooks/manual/
COPY entrypoint /entrypoint

# Permissions, paths, ports, entrypoint
RUN chmod a+x /usr/share/nginx/dehydrated/hooks/manual/route53_hook.rb && \
    chmod a+x /entrypoint

ENV PATH $PATH:/etc/letsencrypt/dehydrated

CMD ["/entrypoint"]
