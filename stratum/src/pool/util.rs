// Copyright 2017 The Grin Developers
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

//! header manipulation utility functions

use byteorder::{BigEndian, ByteOrder};
use rand::{self, Rng};


use std::fmt::Write;
use std::num;

pub fn header_data(pre_nonce: &str, post_nonce: &str, nonce: u64) -> (Vec<u8>, u32) {
	// Turn input strings into vectors
	let mut pre_vec = from_hex_string(pre_nonce);
	let mut post_vec = from_hex_string(post_nonce);

	let sec_scaling_bytes = &pre_vec.clone()[pre_vec.len()-4..pre_vec.len()];
	let sec_scaling = BigEndian::read_u32(&sec_scaling_bytes);

	let mut nonce_bytes = [0; 8];
	BigEndian::write_u64(&mut nonce_bytes, nonce);
	let mut nonce_vec = nonce_bytes.to_vec();

	// Generate new header
	pre_vec.append(&mut nonce_vec);
	pre_vec.append(&mut post_vec);

	(pre_vec, sec_scaling)
}

pub fn get_next_header_data(pre_nonce: &str, post_nonce: &str) -> (u64, Vec<u8>, u32) {
	let nonce: u64 = rand::OsRng::new().unwrap().gen();
	let (hd, sec_scaling) = header_data(pre_nonce, post_nonce, nonce);
	(nonce, hd, sec_scaling)
}

/// Helper to convert a hex string
pub fn from_hex_string(in_str: &str) -> Vec<u8> {
	let mut bytes = Vec::new();
	for i in 0..(in_str.len() / 2) {
		let res = u8::from_str_radix(&in_str[2 * i..2 * i + 2], 16);
		match res {
			Ok(v) => bytes.push(v),
			Err(e) => println!("Problem with hex: {}", e),
		}
	}
	bytes
}

// From grin-miner util
/// Encode the provided bytes into a hex string
pub fn to_hex(bytes: Vec<u8>) -> String {
	let mut s = String::new();
	for byte in bytes {
		write!(&mut s, "{:02x}", byte).expect("Unable to write");
	}
	s
}

/// Decode a hex string into bytes.
pub fn from_hex(hex_str: String) -> Result<Vec<u8>, num::ParseIntError> {
	let hex_trim = if &hex_str[..2] == "0x" {
		hex_str[2..].to_owned()
	} else {
		hex_str.clone()
	};
	split_n(&hex_trim.trim()[..], 2)
		.iter()
		.map(|b| u8::from_str_radix(b, 16))
		.collect::<Result<Vec<u8>, _>>()
}

fn split_n(s: &str, n: usize) -> Vec<&str> {
	(0..(s.len() - n + 1) / 2 + 1)
		.map(|i| &s[2 * i..2 * i + n])
		.collect()
}
