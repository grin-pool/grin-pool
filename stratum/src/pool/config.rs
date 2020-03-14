// Copyright 2018 Blade M. Doyle
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#[macro_use]
use serde_derive;
use std::fs::File;
use std::io::prelude::*;
use std::env;
use toml;

const CONFIG_FILE_NAME: &'static str = "grin-pool.toml";

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub grin_pool: PoolConfig,
    pub grin_node: NodeConfig,
    pub workers: WorkerConfig,
    pub redis: RedisConfig,
}

#[derive(Debug, Deserialize, Clone)]
pub struct PortDifficulty {
    pub port: u64,
    pub difficulty: u64,
}

#[derive(Debug, Deserialize, Clone)]
pub struct PoolConfig {
    pub log_dir: String,
    pub pool: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct WorkerConfig {
    pub listen_address: String,
    pub port_difficulty: PortDifficulty,
}

#[derive(Debug, Deserialize, Clone)]
pub struct NodeConfig {
    pub address: String,
    pub api_port: u64,
    pub stratum_port: u64,
    pub login: String,
    pub password: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct RedisConfig {
    pub address: String,
    pub port: u64,
}


pub fn read_config() -> Config {
    let mut config_file = File::open(CONFIG_FILE_NAME).expect("Config file not found");
    let mut toml_str = String::new();
    config_file
        .read_to_string(&mut toml_str)
        .expect("Failure while reading config file");
    let mut config: Config = toml::from_str(&toml_str).unwrap();

    // Environment Variable Overrides
    match env::var("DIFFICULTY") {
        Ok(difficulty) => {
            config.workers.port_difficulty.difficulty = difficulty.parse().unwrap() ;
            println!("env difficulty: {:?}", config);

        }
        Err(e) => {}
    }

    match env::var("GRIN_ADDRESS") {
        Ok(address) => {
            config.grin_node.address = address;
            println!("env address: {:?}", config);
        }
        Err(e) => {}
    }

    match env::var("REDIS_PORT") {
        Ok(port) => {
            config.redis.port = port.parse::<u64>().unwrap();
            println!("env redis: {:?}", config.redis);
        }
        Err(e) => {}
    }

    match env::var("POOL") {
        Ok(pool) => {
            config.grin_pool.pool = pool.trim().to_string();
            println!("env pool: {:?}", config.grin_pool);
        }
        Err(e) => {}
    }

    return config.clone();
}
