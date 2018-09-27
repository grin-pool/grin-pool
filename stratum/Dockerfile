# Multistage docker build, requires docker 17.05

# builder stage
FROM rust:1.26 as builder

RUN set -ex && \
    apt-get update && \
    apt-get --no-install-recommends --yes install \
        clang \
        libclang-dev \
        llvm-dev \
        libncurses5 \
        libncursesw5 \
        cmake \
        git

WORKDIR /stratum

# Copying grin-pool source
COPY src/. /stratum/src/
COPY grin-pool.toml Cargo.toml /stratum/

# Building grin-pool
RUN cargo build

# runtime stage
FROM debian:9.4

WORKDIR /stratum
COPY --from=builder /stratum/target/*/grin-pool /usr/local/bin/
COPY grin-pool.toml /usr/local/bin/

ENV RUST_BACKTRACE=1
ENV PATH=/usr/local/bin:$PATH
EXPOSE 3333
CMD ["/usr/local/bin/grin-pool"]
