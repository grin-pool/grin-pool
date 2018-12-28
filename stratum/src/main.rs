// Copyright 2018 Blade M. Doyle
//
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

//! Mining Stratum Pool

#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate serde_json;
extern crate bufstream;
#[macro_use]
extern crate slog;
extern crate slog_async;
extern crate slog_term;
extern crate time;
#[macro_use]
extern crate lazy_static;
#[macro_use]
extern crate toml;
extern crate sha2;
#[macro_use]
extern crate error_chain;
extern crate kafka;

use bufstream::BufStream;
use std::error::Error;
use std::io::BufRead;
use std::io::{ErrorKind, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::{Arc, Mutex, RwLock};
use std::thread;
use std::time::Duration;
use std::time::SystemTime;

mod pool;
use pool::config;
use pool::logger::LOGGER;
use pool::pool::Pool;

fn main() {
    warn!(LOGGER, "Startng Grin-Pool");

    let config = config::read_config();

    println!("{:?}", config);

    let mut my_pool = Pool::new(config);
    my_pool.run();
}
