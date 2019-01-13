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

use pool::config::{Config, NodeConfig, PoolConfig, WorkerConfig};
use pool::logger::LOGGER;
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
}

impl Server {
    /// Creates a new Stratum Server Connection.
    pub fn new(cfg: Config) -> Server {
        Server {
            id: "Pool".to_string(),
            config: cfg,
            stream: None,
            protocol: StratumProtocol::new(),
            error: false,
            job: JobTemplate::new(),
            status: WorkerStatus::new("Pool".to_string()),
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
            LOGGER,
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
    pub fn request_status(&mut self, stream: &mut BufStream<TcpStream>) -> Result<(), String> {
        match self.stream {
            Some(ref mut stream) => {
                trace!(LOGGER, "{} - Requesting status", self.id);
                return self.protocol.send_request(
                    stream,
                    "status".to_string(),
                    None,
                    Some(self.id.clone()),
                );
            }
            None => Err("No upstream connection".to_string()),
        }
    }

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
                debug!(LOGGER, "{} - Requesting Login", self.id);
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
                debug!(LOGGER, "{} - Requesting Job Template", self.id);
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
        worker_id: usize,
    ) -> Result<(), String> {
        match self.stream {
            Some(ref mut stream) => {
                let params_value = serde_json::to_value(solution).unwrap();
                debug!(LOGGER, "{} - Submitting a share", self.id);
                return self.protocol.send_request(
                    stream,
                    "submit".to_string(),
                    Some(params_value),
                    Some(worker_id.to_string()),
                );
            }
            None => Err("No upstream connection".to_string()),
        }
    }

    /// Send Keepalive
    pub fn send_keepalive(&mut self) -> Result<(), String> {
        match self.stream {
            Some(ref mut stream) => {
                debug!(LOGGER, "{} - Sending Keepalive", self.id);
                return self.protocol.send_request(
                    stream,
                    "keepalive".to_string(),
                    None,
                    Some(self.id.clone()),
                );
            }
            None => Err("No upstream connection".to_string()),
        }
    }

    //
    // Method to handle responses from the upstream stratum server

    /// Process Messages from the upstream stratum server
    pub fn process_messages(
        &mut self,
        workers: &mut Arc<Mutex<Vec<Worker>>>,
    ) -> Result<String, RpcError> {
        // XXX TODO: With some reasonable rate limiting (like N message per pass)
        return self.process_message(workers);
    }
    pub fn process_message(
        &mut self,
        workers: &mut Arc<Mutex<Vec<Worker>>>,
    ) -> Result<String, RpcError> {
        // Read a message from the upstream
        // Handle the message
        // XXX TODO: Complete adding RPC error results (especially still syncing error)
        match self.stream {
            Some(ref mut stream) => {
                match self.protocol.get_message(stream) {
                    Ok(rpc_msg) => {
                        match rpc_msg {
                            Some(message) => {
                                trace!(
                                    LOGGER,
                                    "{} - Got Message from upstream Server: {:?}",
                                    self.id,
                                    message
                                );
                                let v: serde_json::Value = serde_json::from_str(&message).unwrap();
                                // Is this a response or request?
                                // XXX TODO: Is there a better way? Introspection? Check Value for field?
                                if v["id"] == String::from("Stratum") {
                                    // this is a request
                                    let req: RpcRequest = serde_json::from_str(&message).unwrap();
                                    trace!(
                                        LOGGER,
                                        "{} - Received request type: {}",
                                        self.id,
                                        req.method
                                    );
                                    match req.method.as_str() {
                                        // The upstream stratum server has sent us a new job
                                        "job" => {
                                            let job: JobTemplate = serde_json::from_value(req.params.unwrap()).unwrap();
                                            debug!(
                                                LOGGER,
                                                "{} - Setting new job for height {} job_id {}",
                                                self.id,
                                                job.height,
						job.job_id,
                                            );
                                            self.job = job;
                                            return Ok(req.method.clone());
                                        }
                                        _ => {
                                            // XXX TODO: Unknown request type from the upstream stratum server - log it and continue
                                            debug!(
                                                LOGGER,
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
                                    // This is a response from the upstream Grin Stratum Server
                                    // Here, we are accepting responses to requests we sent on behalf of a worker
                                    // The messages 'id' field contains the worker id this response is for
                                    // We need to process the responses the pool cares about,
                                    // The pool made this request and it will handle responses (so return the results back up)
                                    let res: RpcResponse = serde_json::from_str(&message).unwrap();
                                    debug!(LOGGER, "{} - Received response {:?}", self.id, res);
                                    let mut workers_l = workers.lock().unwrap();
                                    // Get the worker index this response is for
                                    let w_id_usz: usize = match res.id.parse::<usize>() {
                                        Ok(id) => id,
                                        Err(err) => {
                                            let e = RpcError {
                                                code: -1,
                                                message: "Invalid Worker ID".to_string(),
                                            };
                                            return Err(e);
                                        }
                                    };
                                    let w_id: usize = workers_l
                                        .iter()
                                        .position(|ref i| i.id == w_id_usz)
                                        .unwrap();
                                    match res.method.as_str() {
                                        // This is a response to a getjobtemplate request made by the pool
                                        "getjobtemplate" => {
                                            // Could be rpcerror - like "still syncing"
                                            match res.result {
                                                Some(response) => {
                                                    let job: JobTemplate = serde_json::from_value(response).unwrap();
                                                    debug!(
                                                        LOGGER,
                                                        "{} - Setting new job for height {}",
                                                        self.id,
                                                        job.height
                                                    );
                                                    self.job = job;
                                                    return Ok(res.method.clone());
                                                }
                                                None => {
                                                    self.error = true;
                                                    let e: RpcError = serde_json::from_value(res.error.unwrap()).unwrap();
                                                    // XXX TODO: Send response to the worker
                                                    return Err(e);
                                                }
                                            }
                                        }
                                        // This is a response to a login request the pool made to the grin node
                                        // The pool made this request and it will handle responses
                                        "login" => {
                                            match res.result {
                                                Some(response) => {
                                                    // Server accepted our login
                                                    return Ok(res.method.clone());
                                                }
                                                None => {
                                                    // Server did NOT accept our login
                                                    self.error = true;
                                                    let e: RpcError = serde_json::from_value(res.error.unwrap()).unwrap();
                                                    return Err(e);
                                                }
                                            }
                                        }
                                        "status" => {
                                            // XXX TODO: Error checking
                                            self.status =
                                                serde_json::from_value(res.result.unwrap())
                                                    .unwrap();
                                            return Ok(res.method.clone());
                                        }
                                        "submit" => {
                                            // XXX TODO: Error checking
                                            debug!(LOGGER, "w_id = {}", w_id);
                                            match res.result {
                                                Some(response) => {
                                                    // The share was accepted
                                                    debug!(
                                                        LOGGER,
                                                        "setting stats for worker id {:?}", res.id
                                                    );
                                                    workers_l[w_id].status.accepted += 1;
                                                    debug!(LOGGER, "Server accepted our share");
                                                    workers_l[w_id].send_ok(res.method.clone(), res.id);
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
                                                            workers_l[w_id].status.stale += 1;
                                                            debug!(
                                                                LOGGER,
                                                                "Server rejected share as stale"
                                                            );
                                                        }
                                                        _ => {
                                                            workers_l[w_id].status.rejected += 1;
                                                            debug!(
                                                                LOGGER,
                                                                "Server rejected share as invalid"
                                                            );
                                                        }
                                                    }
                                                }
                                            };
                                            return Ok(res.method.clone());
                                        }
                                        "keepalive" => {
                                            // XXX TODO: If its an error
                                            //      Set error state
                                            //      Return error message why
                                            return Ok(res.method.clone());
                                        }
                                        _ => {
                                            // XXX TODO: Unknown reponse type - log it and continue
                                            debug!(
                                                LOGGER,
                                                "{} - Got unknown response type: {}",
                                                self.id,
                                                res.method.as_str()
                                            );
                                            let e = RpcError {
                                                code: -32600,
                                                message: "Invalid Response".to_string(),
                                            };
                                            return Err(e);
                                        }
                                    }
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
