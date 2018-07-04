// Copyright 2018 The Grin Developers
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
use lazy_static;
use std::fs::OpenOptions;
use slog::{Discard, Drain, Duplicate, Level, LevelFilter, Logger};
use std::{panic, thread};
use slog_term;
use slog_async;

use pool::config;

lazy_static! {
  	/// A static reference to the logger itself, accessible from all crates
    pub static ref LOGGER: Logger = {

        let config = config::read_config();
        let log_file_path = config.grin_pool.log_dir + "/" + "grin-pool.log";
	let slog_level_stdout = Level::Debug;
	let slog_level_file = Level::Trace;

	// Terminal output drain
	let terminal_decorator = slog_term::TermDecorator::new().build();
	let terminal_drain = slog_term::FullFormat::new(terminal_decorator).build().fuse();
	let terminal_drain = LevelFilter::new(terminal_drain, slog_level_stdout).fuse();
	let mut terminal_drain = slog_async::Async::new(terminal_drain).build().fuse();

	// File drain
	let file = OpenOptions::new()
		.create(true)
		.write(true)
		.append(true)
		.truncate(false)
		.open(log_file_path)
		.unwrap();

	let file_decorator = slog_term::PlainDecorator::new(file);
	let file_drain = slog_term::FullFormat::new(file_decorator).build().fuse();
	let file_drain = LevelFilter::new(file_drain, slog_level_file).fuse();
	let file_drain_final = slog_async::Async::new(file_drain).build().fuse();

	let composite_drain = Duplicate::new(terminal_drain, file_drain_final).fuse();

	Logger::root(composite_drain, o!())
    };
}
