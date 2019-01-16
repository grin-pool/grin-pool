# Multistage docker build, requires docker 17.05

# builder stage
FROM rust:latest as builder

RUN rustup update && \
    set -ex && \
    apt-get update && \
    apt-get --no-install-recommends --yes install \
        clang \
        libclang-dev \
        llvm-dev \
        libncurses5 \
        libncursesw5 \
        cmake \
        git \
        libssl-dev

WORKDIR /usr/src/grin

# Copying Grin
RUN git clone https://github.com/mimblewimble/grin.git .; git checkout master; git pull;

# Building Grin
RUN cargo build --release

# Update and build grin
RUN touch asxxyyzzzzqyxxxy
RUN git fetch && \
    git pull && \
    git checkout master

# Monkey Patch
RUN sed -i -e 's/127\.0\.0\.1:13420/0.0.0.0:13420/g' wallet/src/command.rs
#COPY stratumserver.rs servers/src/mining/stratumserver.rs

RUN cargo build --release

# Generate configuration
# XXX TODO: REMOVE FOR MAINNET
ENV NET_FLAG "--floonet"
RUN mkdir -p /root/.grin && \
    cd /root/.grin && \
    ln -s . floo && \
    ln -s . main
RUN target/release/grin ${NET_FLAG} server config && \
    echo dummy > dummy && \
    echo dummy >> dummy && \
    target/release/grin ${NET_FLAG} wallet init  < dummy


# runtime stage
FROM docker.mwgrinpool.com:5001/keybase:latest

# XXX TODO: REMOVE FOR MAINNET
ENV NET_FLAG "--floonet"


RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    locales \
    procps \
    libssl-dev \
    vim \
    telnet \
    curl \
    python3 \
      && \
    apt-get autoremove -y && \
    rm -rf /var/cache/apt

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8 

ENV LANG en_US.UTF-8

COPY --from=builder /usr/src/grin/target/release/grin /usr/local/bin/grin
COPY --from=builder /usr/src/grin/grin-server.toml /usr/src/grin/grin-server.toml
COPY --from=builder /root/.grin/grin-wallet.toml /usr/src/grin/grin-wallet.toml

# Update grin-server config
RUN sed -i 's/^db_root = .*$/db_root = "\/server\/.grin"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^api_http_addr = .*$/api_http_addr = "0.0.0.0:13413"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^api_secret_path = .*$/api_secret_path = "\/root\/.grin\/.api_secret"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^archive_mode = .*$/archive_mode = true/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^skip_sync_wait = .*$/skip_sync_wait = false/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^run_tui = .*$/run_tui = false/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^run_test_miner = .*$/run_test_miner = false/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^host = .*$/host = "0.0.0.0"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^port = .*$/port = 13414/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^?peer_max_count = .*$/peer_max_count = 75/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^?peer_min_preferred_count = .*$/peer_min_preferred_count = 15/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^enable_stratum_server = .*$/enable_stratum_server = true/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^stratum_server_addr = .*$/stratum_server_addr = "0.0.0.0:13416"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^attempt_time_per_block = .*$/attempt_time_per_block = 300/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^minimum_share_difficulty = .*$/minimum_share_difficulty = 1/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^wallet_listener_url = .*$/wallet_listener_url = "http:\/\/grinwallet:13415"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^burn_reward = .*$/burn_reward = false/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^log_to_stdout = .*$/log_to_stdout = true/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^stdout_log_level = .*$/stdout_log_level = "Debug"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^log_to_file = .*$/log_to_file = true/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^file_log_level = .*$/file_log_level = "Debug"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^log_file_path = .*$/log_file_path = "\/server\/grin.log"/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^log_file_append = .*$/log_file_append = true/' /usr/src/grin/grin-server.toml && \
    sed -i 's/^log_max_size = .*$/log_max_size = 16777216/' /usr/src/grin/grin-server.toml

# Update grin-wallet config
RUN sed -i 's/^api_listen_interface = .*$/api_listen_interface = "0.0.0.0"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^api_listen_port = .*$/api_listen_port = 13415/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^api_secret_path = .*$/api_secret_path = "\/root\/.grin\/.api_secret"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^node_api_secret_path = .*$/node_api_secret_path = "\/root\/.grin\/.api_secret"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^check_node_api_http_addr = .*$/check_node_api_http_addr = "http:\/\/grin:13413"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^data_file_dir = .*$/data_file_dir = "\/wallet\/wallet_data"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^keybase_notify_ttl = .*$/keybase_notify_ttl = 1440/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^log_to_stdout = .*$/log_to_stdout = true/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^stdout_log_level = .*$/stdout_log_level = "Debug"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^log_to_file = .*$/log_to_file = true/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^file_log_level = .*$/file_log_level = "Debug"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^log_file_path = .*$/log_file_path = "\/wallet\/grin-wallet.log"/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^log_file_append = .*$/log_file_append = true/' /usr/src/grin/grin-wallet.toml && \
    sed -i 's/^log_max_size = .*$/log_max_size = 16777216/' /usr/src/grin/grin-wallet.toml 
    

# floonet ports
EXPOSE 13413
EXPOSE 13414
EXPOSE 13415
EXPOSE 13416

# mainnet ports
EXPOSE 3413
EXPOSE 3414
EXPOSE 3415
EXPOSE 3416

COPY run.sh /
COPY run-wallet.sh /
COPY libheath.py /
CMD ["/run.sh"]
