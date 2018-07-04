FROM ubuntu:17.10

# Reference: https://howtomine.co/2018/01/11/how-to-mine-grin-testnet/

RUN set -e && \
  apt-get update -q && \
  apt-get install -q -y --no-install-recommends ca-certificates curl && \
  apt-get install -y software-properties-common && \
  apt-get install -y build-essential python python-pip g++ git cmake libtool autotools-dev automake pkg-config libssl-dev libevent-dev bsdmainutils clang-3.8 cargo

#RUN set -e && \
#    apt-get install -q -y librocksdb-dev
RUN apt-get install -q -y  libncurses5-dev libncursesw5-dev \
                           net-tools vim psmisc && \
    pip install python-dateutil && \
    pip install pytz

ENV PATH=/root/.cargo/bin:${PATH}
ENV LANG=C.UTF-8

# Install Rust
RUN curl https://sh.rustup.rs -sSf > irsut.sh && \
    sh ./irsut.sh -y && \
    rustc -V && \
    rustup component add --toolchain stable rustfmt-preview

RUN cd / && \
    git clone https://github.com/mimblewimble/grin.git && \
    cd /grin && \
    git checkout master && \
    git pull && \
    cargo build --release

RUN touch REBUILD_x
RUN cd /grin && \
    git checkout master && \
    git pull && \
    cargo build --release

ENV PATH=/grin/target/release:/grin/target/debug:${PATH}
ENV TERM=vt100

WORKDIR /grin

COPY run.sh /
CMD ["/run.sh"]


