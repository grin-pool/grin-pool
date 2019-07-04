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
use std::fs::OpenOptions;
use std::{panic, thread};
use backtrace::Backtrace;

use log::{LevelFilter, Record};
use log4rs;
use log4rs::append::console::ConsoleAppender;
use log4rs::append::file::FileAppender;
use log4rs::append::rolling_file::{
	policy::compound::roll::fixed_window::FixedWindowRoller,
	policy::compound::trigger::size::SizeTrigger, policy::compound::CompoundPolicy,
	RollingFileAppender,
};
use log4rs::append::Append;
use log4rs::config::{Appender, Config, Root};
use log4rs::encode::pattern::PatternEncoder;
use log4rs::filter::{threshold::ThresholdFilter, Filter, Response};



use pool::config;

//lazy_static! {

pub fn init_logger() {

    let config = config::read_config();
    let log_file_path = config.grin_pool.log_dir + "/" + "grin-pool.log";
    let level_stdout = LevelFilter::Trace;
    let level_file = LevelFilter::Warn;
    let level_minimum = level_stdout;
    let size = 16777216; // XXX TODO GET FROM CONFIG

    let stdout = ConsoleAppender::builder()
			.encoder(Box::new(PatternEncoder::default()))
			.build();

		let mut root = Root::builder();

		let mut appenders = vec![];

		let filter = Box::new(ThresholdFilter::new(level_stdout));
		appenders.push(
			Appender::builder()
				.filter(filter)
				.build("stdout", Box::new(stdout)),
		);

		root = root.appender("stdout");

		// If maximum log size is specified, use rolling file appender
		// or use basic one otherwise
		let filter = Box::new(ThresholdFilter::new(level_file));
		let file: Box<Append> = {
			let roller = FixedWindowRoller::builder()
				.build(&format!("{}.{{}}.gz", log_file_path), 32)
				.unwrap();
			let trigger = SizeTrigger::new(size);

			let policy = CompoundPolicy::new(Box::new(trigger), Box::new(roller));

			Box::new(
				RollingFileAppender::builder()
					.append(true)
					.encoder(Box::new(PatternEncoder::new("{d} {l} {M} - {m}{n}")))
					.build(log_file_path, Box::new(policy))
					.unwrap(),
			)
		};

		appenders.push(
			Appender::builder()
				.filter(filter)
				.build("file", file),
		);
		root = root.appender("file");

		let config = Config::builder()
			.appenders(appenders)
			.build(root.build(level_minimum))
			.unwrap();

		let _ = log4rs::init_config(config).unwrap();

		info!(
			"log4rs is initialized, file level: {:?}, stdout level: {:?}, min. level: {:?}",
			level_file, level_stdout, level_minimum
        );

        panic::set_hook(Box::new(|info| {
    		let backtrace = Backtrace::new();

    		let thread = thread::current();
    		let thread = thread.name().unwrap_or("unnamed");

    		let msg = match info.payload().downcast_ref::<&'static str>() {
    			Some(s) => *s,
    			None => match info.payload().downcast_ref::<String>() {
    				Some(s) => &**s,
    				None => "Box<Any>",
    			},
    		};

    		match info.location() {
    			Some(location) => {
    				error!(
    					"\nthread '{}' panicked at '{}': {}:{}{:?}\n\n",
    					thread,
    					msg,
    					location.file(),
    					location.line(),
    					backtrace
    				);
    			}
    			None => error!("thread '{}' panicked at '{}'{:?}", thread, msg, backtrace),
    		}
        }));
}
