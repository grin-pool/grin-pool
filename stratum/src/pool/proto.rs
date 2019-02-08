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

//! Mining Stratum Server JSON RPC Protocol
//!
//! Offers methods to send / recv messages with the stratum
//! workers and servers via JSON RPC.

use bufstream::BufStream;
use serde_json;
use serde_json::Value;
use std::io::BufRead;
use std::io::{ErrorKind, Write};
use std::net::TcpStream;

use pool::logger::LOGGER;

// ----------------------------------------
// RPC Messages
//

// XXX TODO: Revisit all uses of "pub" in the protocol structs?

#[derive(Serialize, Deserialize, Debug)]
pub struct RpcRequest {
    pub id: String,
    jsonrpc: String,
    pub method: String,
    pub params: Option<Value>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct RpcResponse {
    pub id: String,
    jsonrpc: String,
    pub method: String,
    pub result: Option<Value>,
    pub error: Option<Value>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RpcError {
    pub code: i32,
    pub message: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct LoginParams {
    pub login: String,
    pub pass: String,
    pub agent: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct SubmitParams {
    pub height: u64,
    pub job_id: u64,
    pub nonce: u64,
    pub edge_bits: u32,
    pub pow: Vec<u64>,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct JobTemplate {
    pub height: u64,
    pub job_id: u64,
    pub difficulty: u64,
    pub pre_pow: String,
}

impl JobTemplate {
    pub fn new() -> JobTemplate {
        JobTemplate {
            height: 0,
            job_id: 0,
            difficulty: 0,
            pre_pow: "".to_string(),
        }
    }
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct WorkerStatus {
    pub id: String,
    pub height: u64,
    pub difficulty: u64,
    pub accepted: u64,
    pub rejected: u64,
    pub stale: u64,
}

impl WorkerStatus {
    pub fn new(id: String) -> WorkerStatus {
        WorkerStatus {
            id: id,
            height: 0,
            difficulty: 0,
            accepted: 0,
            rejected: 0,
            stale: 0,
        }
    }
}

// --------------------------------
// A Staratum Protocol Interface

pub struct StratumProtocol {
    id: String,
}

impl StratumProtocol {
    /// Creates a new Protocol instance for communication with a Stratum Server
    pub fn new() -> StratumProtocol {
        StratumProtocol {
            id: String::from("proto"),
        }
    }

    /// Read a message from the stream
    fn read_message(
        &mut self,
        stream: &mut BufStream<TcpStream>,
    ) -> Result<Option<String>, String> {
        // Read and return a single message or None
        let mut line = String::new();
        match stream.read_line(&mut line) {
            Ok(_) => {
                // warn!(LOGGER, "XXX DEBUG - line read: {:?}", line);
                // stream is not returning a proper error on disconnect
                if line == "" {
                    return Err(format!("{} - Connection Error 1: Disconnected", self.id));
                }
                return Ok(Some(line));
            }
            Err(ref e) if e.kind() == ErrorKind::WouldBlock => {
                // Not an error, just no messages ready
                return Ok(None);
            }
            Err(e) => {
                error!(LOGGER, "{} - Connection Error 1a: {}", self.id, e);
                return Err(format!("{}", e));
            }
        }
    }

    /// Write a message to the stream and flush
    pub fn write_message(
        &mut self,
        message_in: String,
        stream: &mut BufStream<TcpStream>,
    ) -> Result<(), String> {
        let mut message = message_in.clone();
        if !message.ends_with("\n") {
            message += "\n";
        }
        match stream.write(message.as_bytes()) {
            Ok(_) => match stream.flush() {
                Ok(_) => {}
                Err(e) => {
                    error!(LOGGER, "{} - Connection Error 2: {}", self.id, e);
                    return Err(format!("{}", e));
                }
            },
            Err(e) => {
                error!(LOGGER, "{} - Connection Error 2a: {}", self.id, e);
                return Err(format!("{}", e));
            }
        }
        return Ok(());
    }

    /// Get a message from the upstream
    pub fn get_message(
        &mut self,
        stream: &mut BufStream<TcpStream>,
    ) -> Result<Option<String>, String> {
        // XXX TODO: Verify this is a valid message before returning it
        return self.read_message(stream);
    }

    /// Send a Request
    // params is the method parameters in serde_json string
    pub fn send_request(
        &mut self,
        stream: &mut BufStream<TcpStream>,
        method: String,
        params: Option<Value>,
        worker_id: Option<String>,
    ) -> Result<(), String> {
        let request_id = match worker_id {
            None => "".to_string(),
            Some(id) => id,
        };
        let req = RpcRequest {
            id: request_id.clone(),
            jsonrpc: "2.0".to_string(),
            method: method,
            params: Some(serde_json::to_value(params).unwrap()),
        };
        let req_str = serde_json::to_string(&req).unwrap();
        trace!(
            LOGGER,
            "{} for {} - Requesting: {}",
            self.id,
            request_id,
            req_str
        );
        return self.write_message(req_str, stream);
    }

    /// Send a Response
    pub fn send_response(
        &mut self,
        stream: &mut BufStream<TcpStream>,
        method: String,
        result: Value,
        worker_id: Option<String>,
    ) -> Result<(), String> {
        let res = RpcResponse {
            id: worker_id.clone().unwrap(),
            jsonrpc: "2.0".to_string(),
            method: method,
            result: Some(result),
            error: None,
        };
        let res_str = serde_json::to_string(&res).unwrap();
        trace!(
            LOGGER,
            "{} for {} - Responding: {}",
            self.id,
            worker_id.unwrap(),
            res_str
        );
        return self.write_message(res_str, stream);
    }

    /// Send an Error Response
    pub fn send_error_response(
        &mut self,
        stream: &mut BufStream<TcpStream>,
        method: String,
        error: RpcError,
    ) -> Result<(), String> {
        let res = RpcResponse {
            id: self.id.clone(),
            jsonrpc: "2.0".to_string(),
            method: method,
            result: None,
            error: Some(serde_json::to_value(error).unwrap()),
        };
        let res_str = serde_json::to_string(&res).unwrap();
        trace!(LOGGER, "{} - Responding with Error: {}", self.id, res_str);
        return self.write_message(res_str, stream);
    }
}
