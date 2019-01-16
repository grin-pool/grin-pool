# Multistage docker build, requires docker 17.05

# builder stage
FROM rust:latest as builder

RUN set -ex && \
    apt-get update && \
    apt-get --no-install-recommends --yes install \
        clang \
        libclang-dev \
        llvm-dev \
        libncurses5 \
        libncursesw5 \
        libssl-dev \
        libssl1.1 \
        cmake \
        git \
        vim \
        net-tools \
        procps
        

WORKDIR /stratum


RUN touch x
# Copying grin-pool source
COPY src/. /stratum/src/
COPY grin-pool.toml Cargo.toml /stratum/

# Building grin-pool
RUN cargo build

# runtime stage
FROM debian:9.4

RUN set -ex && \
    apt-get update && \
    apt-get --no-install-recommends --yes install \
        libssl-dev \
        libssl1.1

WORKDIR /stratum
COPY --from=builder /stratum/target/*/grin-pool /usr/local/bin/
COPY grin-pool.toml /usr/local/bin/
COPY grin-pool.toml /stratum
COPY run.sh /

ENV RUST_BACKTRACE=1
ENV PATH=/usr/local/bin:$PATH
EXPOSE 3333
CMD ["/run.sh"]
