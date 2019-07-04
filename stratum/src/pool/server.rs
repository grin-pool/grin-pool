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

//! Mining Stratum Server Connection
//!
//! An upstream grin stratum server
//!

use bufstream::BufStream;
use serde_json;
use serde_json::Value;
use std::net::{Shutdown, TcpStream};
use std::sync::{Arc, Mutex, RwLock};
use std::{thread, time};
use std::collections::HashMap;


use pool::config::{Config, NodeConfig, PoolConfig, WorkerConfig};
use pool::proto::{JobTemplate, LoginParams, RpcError, StratumProtocol, SubmitParams, WorkerStatus};
use pool::proto::{RpcRequest, RpcResponse};
use pool::worker::Worker;

// ----------------------------------------
// Server Object - our connection to a stratum server - a grin node

pub struct Server {
    id: String,
    config: Config,
    stream: Option<BufStream<TcpStream>>,
    protocol: StratumProtocol,
    error: bool,
    pub job: JobTemplate,
    status: WorkerStatus,
    buffer: String,
}

impl Server {
    /// Creates a new Stratum Server Connection.
    pub fn new(cfg: Config) -> Server {
        Server {
            id: "MWGrinPool".to_string(),
            config: cfg,
            stream: None,
            protocol: StratumProtocol::new(),
            error: false,
            job: JobTemplate::new(),
            status: WorkerStatus::new("MWGrinPool".to_string()),
            buffer: String::with_capacity(4096),
        }
    }

    /// Connect to an upstream Grin Stratum Server
    /// Request Login and Job Request
    pub fn connect(&mut self) -> Result<(), String> {
        // Only connect if we are not already connected
        if !self.error && self.stream.is_some() {
            return Ok(());
        }
        let grin_stratum_url = self.config.grin_node.address.clone() + ":"
            + &self.config.grin_node.stratum_port.to_string();
        warn!(
            "{} - Connecting to upstream stratum server at {}",
            self.id,
            grin_stratum_url.to_string()
        );
        match TcpStream::connect(grin_stratum_url.to_string()) {
            Ok(conn) => {
                let _ = conn.set_nonblocking(true)
                    .expect("set_nonblocking call failed");
                self.stream = Some(BufStream::new(conn));
                self.error = false;
            }
            Err(e) => {
                self.error = true;
                return Err(e.to_string());
            }
        };
        // Send login
        match self.log_in() {
            Ok(_) => {}
            Err(e) => {
                self.error = true;
                return Err(e.to_string());
            }
        };
        // Send job request
        match self.request_job() {
            Ok(_) => {}
            Err(e) => {
                self.error = true;
                return Err(e.to_string());
            }
        };
        return Ok(());
    }

    /// Request status from the upstream Grin Stratum server - this is *pool* status (not individual
    /// worker status)
    // Currently unused
//    pub fn request_status(&mut self, stream: &mut BufStream<TcpStream>) -> Result<(), String> {
//        match self.stream {
//            Some(ref mut stream) => {
//                trace!("{} - Requesting status", self.id);
//                return self.protocol.send_request(
//                    stream,
//                    "status".to_string(),
//                    None,
//                    Some(self.id.clone()),
//                );
//            }
//            None => Err("No upstream connection".to_string()),
//        }
//    }

    /// Send our login info to the upstream stratum server
    fn log_in(&mut self) -> Result<(), String> {
        match self.stream {
            Some(ref mut stream) => {
                let login_params = LoginParams {
                    login: self.config.grin_node.login.clone().to_string(),
                    pass: self.config.grin_node.password.clone().to_string(),
                    agent: self.id.clone(),
                };
                let params_value = serde_json::to_value(login_params).unwrap();
                trace!("{} - Requesting Login", self.id);
                return self.protocol.send_request(
                    stream,
                    "login".to_string(),
                    Some(params_value),
                    Some(self.id.clone()),
                );
            }
            None => Err("No upstream connection".to_string()),
        }
    }

    /// Request a new job template from the upstream Grin Stratum server
    fn request_job(&mut self) -> Result<(), String> {
        match self.stream {
            Some(ref mut stream) => {
                trace!("{} - Requesting Job Template", self.id);
                return self.protocol.send_request(
                    stream,
                    "getjobtemplate".to_string(),
                    None,
                    Some(self.id.clone()),
                );
            }
            None => Err("No upstream connection".to_string()),
        }
    }

    /// Submit a workers share as a valid POW solution
    pub fn submit_share(
        &mut self,
        solution: &SubmitParams,
        worker_id: String,
    ) -> Result<(), String> {
        match self.stream {
            Some(ref mut stream) => {
                let params_value = serde_json::to_value(solution).unwrap();
                trace!("{} - Submitting a share", self.id);
                return self.protocol.send_request(
                    stream,
                    "submit".to_string(),
                    Some(params_value),
                    Some(self.id.clone()),
                );
            }
            None => Err("No upstream connection".to_string()),
        }
    }

    /// Send Keepalive
    // Not currently used
//    pub fn send_keepalive(&mut self) -> Result<(), String> {
//        match self.stream {
//            Some(ref mut stream) => {
//                trace!("{} - Sending Keepalive", self.id);
//                return self.protocol.send_request(
//                    stream,
//                    "keepalive".to_string(),
//                    None,
//                    Some(self.id.clone()),
//                );
//            }
//            None => Err("No upstream connection".to_string()),
//        }
//    }



    /// Process Messages from the upstream stratum server
    // Method to handle responses from the upstream stratum server
    pub fn process_messages(
        &mut self,
        workers: &mut Arc<Mutex<HashMap<String, Worker>>>,
    ) -> Result<String, RpcError> {
        // XXX TODO: With some reasonable rate limiting (like N message per pass)
        return self.process_message(workers);
    }
    pub fn process_message(
        &mut self,
        workers: &mut Arc<Mutex<HashMap<String, Worker>>>,
    ) -> Result<String, RpcError> {
        // Read a message from the upstream
        // Handle the message
        // XXX TODO: Complete adding RPC error results (especially still syncing error)
        match self.stream {
            Some(ref mut stream) => {
                match self.protocol.get_message(stream, &mut self.buffer) {
                    Ok(rpc_msg) => {
                        match rpc_msg {
                            Some(message) => {
                                trace!(
                                    "{} - Got Message from upstream Server: {:?}",
                                    self.id,
                                    message
                                );
                                let v: serde_json::Value = match serde_json::from_str(&message) {
                                    Ok(r) => r,
                                    Err(e) => {
                                        // Likely caused by broken connection
                                        self.error = true;
                                        let err_msg = format!("Invalid message from server: {}", e);
                                        let err = RpcError {
                                            code: -32600,
                                            message: err_msg,
                                        };
                                        return Err(err);
                                    }
                                };
                                // Is this a response or request?
                                if v["method"] == String::from("job") {
                                    // This is a REQUEST to start a new JOB
                                    let req: RpcRequest = match serde_json::from_str(&message) {
                                        Ok(r) => r,
                                        Err(e) => {
                                            let err_msg = format!("Invalid RpcRequest from server: {}", e);
                                            let err = RpcError {
                                                code: -32600,
                                                message: err_msg,
                                            };
                                            return Err(err);
                                        }
                                    };
                                    trace!(
                                        "{} - Received request type: {}",
                                        self.id,
                                        req.method
                                    );
                                    match req.method.as_str() {
                                        // The upstream stratum server has sent us a new job
                                        "job" => {
                                            let job: JobTemplate = match serde_json::from_value(req.params.unwrap()) {
                                                Ok(r) => r,
                                                Err(e) => {
                                                    let err_msg = format!("Invalid job request from server: {}", e);
                                                    let err = RpcError {
                                                        code: -32600,
                                                        message: err_msg,
                                                    };
                                                    return Err(err);
                                                }
                                            };
                                            debug!(
                                                "{} - Setting new job for height {} job_id {}",
                                                self.id,
                                                job.height,
                                                job.job_id,
                                            );
                                            self.job = job; // The pool will see the job changed and send to workers
                                            return Ok(req.method.clone());
                                        }
                                        _ => {
                                            // Unknown request type from the upstream stratum server - log it and continue
                                            error!(
                                                "{} - Pool server got unknown request type: {}",
                                                self.id,
                                                req.method.as_str()
                                            );
                                            let e = RpcError {
                                                code: -32601,
                                                message: ["Method not found: ", &req.method]
                                                    .join("")
                                                    .to_string(),
                                            };
                                            return Err(e);
                                        }
                                    };
                                } else {
                                    // This is a RESPONSE from the upstream Grin Stratum Server
                                    // Here, we are accepting responses to requests we sent on behalf of a worker
                                    // The messages 'id' field contains the worker.id+worker.worker_id this response is for
                                    // We need to process the responses the pool cares about,
                                    // The pool made this request and it will handle responses (so return the results back up)
                                    let res: RpcResponse = match serde_json::from_str(&message) {
                                        Ok(r) => r,
                                        Err(e) => {
                                            let err_msg = format!("Invalid RpcResponse from server: {}", e);
                                            let err = RpcError {
                                                code: -32600,
                                                message: err_msg,
                                            };
                                            return Err(err);
                                        }
                                    };
                                    trace!("{} - Received response {:?}", self.id, res);
                                    // Get the worker this response is for
                                    let worker_id = match res.id.parse::<String>() {
                                        Ok(id) => id,
                                        Err(err) => {
                                            let e = RpcError {
                                                code: -1,
                                                message: "Invalid Worker ID".to_string(),
                                            };
                                            return Err(e);
                                        }
                                    };
                                    // First check if this message is for us, rather than a worker
                                    if worker_id == self.id {
                                        trace!("RESPOPNSE for MWGRINPOOL: {}", worker_id);
                                        match res.method.as_str() {
                                            "getjobtemplate" => {
                                                // The upstream stratum server has sent us a new job
                                                // This could be an error result - ex: "Node is syncing - Please wait"
                                                let result: Value = match res.result {
                                                    Some(r) => r,
                                                    None => {
                                                        let err_msg = format!("Error result: {}", res.error.unwrap());
                                                        let err = RpcError {
                                                            code: -32600,
                                                            message: err_msg,
                                                        };
                                                        return Err(err);
                                                    }
                                                };
                                                let job: JobTemplate = match serde_json::from_value(result) {
                                                    Ok(r) => r,
                                                    Err(e) => {
                                                        let err_msg = format!("Invalid jobtemplate from server: {}", e);
                                                        let err = RpcError {
                                                            code: -32600,
                                                            message: err_msg,
                                                        };
                                                        return Err(err);
                                                    }
                                                };
                                                debug!(
                                                    "{} - Setting new job for height {} job_id {}",
                                                    self.id,
                                                    job.height,
                                                    job.job_id,
                                                );
                                                self.job = job;
                                                return Ok(res.method.clone());
                                            }
                                            "login" => {
                                                trace!(
                                                    "{} - Upstream server accepted our login",
                                                    self.id,
                                                );
                                                return Ok(res.method.clone());
                                            }
                                            "submit" => {
                                                // XXX TODO: Error checking
                                                // Debug print this method
                                                trace!("IN rpc method: {}", res.method.as_str());
                                                match res.result {
                                                    Some(response) => {
                                                        // The share was accepted
                                                        debug!(
                                                            "setting stats for worker id {:?}", res.id
                                                        );
                                                        self.status.accepted += 1;
                                                        trace!("Upstream Server accepted our share");
                                                    }
                                                    None => {
                                                        // The share was not accepted, check RpcError.code for reason
                                                        // -32701: Node is syncing
                                                        // -32501: Share rejected due to low difficulty
                                                        // -32502: Failed to validate solution
                                                        // -32503: Solution submitted too late
                                                        // XXX TODO - handle more cases?
                                                        let e: RpcError = serde_json::from_value(res.error.unwrap()).unwrap();
                                                        match e.code {
                                                            -32503 => {
                                                                self.status.stale += 1;
                                                                debug!(
                                                                    "Server rejected share as stale"
                                                                );
                                                            }
                                                            _ => {
                                                                self.status.rejected += 1;
                                                                debug!(
                                                                    "Server rejected share as invalid"
                                                                );
                                                            }
                                                        }
                                                    }
                                                };
                                                return Ok(res.method.clone());
                                            }
                                            _ => {
                                                // XXX TODO: Response to unknown request type from the upstream stratum server - log it and continue
                                                error!(
                                                    "{} - Pool server got unknown response type: {}",
                                                    self.id,
                                                    res.method.as_str()
                                                );
                                                let e = RpcError {
                                                    code: -32601,
                                                    message: ["Method not found: ", &res.method]
                                                        .join("")
                                                        .to_string(),
                                                };
                                                return Err(e);
                                            }
                                        };
                                        return Ok(res.method.clone());
                                    }
                                    // This is a RESPONSE for a WORKER
                                    // There are no longer worker responses, we do all share validation
                                    // and responding to workers from the pool.
                                    let e = RpcError {
                                        code: -32600,
                                        message: "Invalid Response - No worker response should happen".to_string(),
                                    };
                                    return Err(e);
                                }
                            }
                            None => {
                                return Ok("None".to_string());
                            } // Not an error, just no messages for us right now
                        }
                    }
                    Err(e) => {
                        self.error = true;
                        let e = RpcError {
                            code: -32600,
                            message: "Invalid Response".to_string(),
                        };
                        return Err(e);
                    }
                }
            }
            None => {
                self.error = true;
                let e = RpcError {
                    code: -32500,
                    message: "No upstream connection".to_string(),
                };
                return Err(e);
            }
        }
        //return Ok("unknown".to_string());
    }
}
