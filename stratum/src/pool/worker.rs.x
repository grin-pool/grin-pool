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

//! Mining Stratum Worker
//!
//! A single mining worker (the pool manages a vec of Workers)
//!

use bufstream::BufStream;
use serde_json;
use serde_json::Value;
use std::net::TcpStream;

use pool::logger::LOGGER;
use pool::proto::RpcRequest;
use pool::proto::{JobTemplate, LoginParams, StratumProtocol, SubmitParams, WorkerStatus};

// ----------------------------------------
// Worker Object - a connected stratum client - a miner

#[derive(Debug)]
pub struct WorkerConfig {}

pub struct Worker {
    pub id: usize,
    login: Option<LoginParams>,
    stream: BufStream<TcpStream>,
    protocol: StratumProtocol,
    error: bool,
    authenticated: bool,
    pub status: WorkerStatus,       // Runing totals
    pub block_status: WorkerStatus, // Totals for current block
    shares: Vec<SubmitParams>,
    pub needs_job: Option<String>,
}

impl Worker {
    /// Creates a new Stratum Worker.
    pub fn new(id: usize, stream: BufStream<TcpStream>) -> Worker {
        Worker {
            id: id,
            login: None,
            stream: stream,
            protocol: StratumProtocol::new(),
            error: false,
            authenticated: false,
            status: WorkerStatus::new(id.to_string()),
            block_status: WorkerStatus::new(id.to_string()),
            shares: Vec::new(),
            needs_job: id.to_string(),
        }
    }

    /// Is the worker in error state?
    pub fn error(&self) -> bool {
        return self.error;
    }

    /// get the id
    pub fn id(&self) -> usize {
        return self.id;
    }

    /// Get worker login
    pub fn login(&self) -> String {
        match self.login {
            None => "None".to_string(),
            Some(ref login) => login.login.clone(),
        }
    }

    /// Set job difficulty
    pub fn set_difficulty(&mut self, new_difficulty: u64) {
        self.status.difficulty = new_difficulty;
    }

    /// Set job height
    pub fn set_height(&mut self, new_height: u64) {
        self.status.height = new_height;
    }

    /// Send a job request to the worker
    pub fn send_job_request(&mut self, job: &mut JobTemplate) -> Result<(), String> {
        trace!(LOGGER, "Worker {} - Sending a job request downstream", self.id);
        job.difficulty = self.status.difficulty;
        self.needs_job = None;
        let job_value = serde_json::to_value(job).unwrap();
        return self.protocol.send_request(
            &mut self.stream,
            "job".to_string(),
            job_value,
            self.id.to_string(),
        );
    }

    /// Send a job response to the worker
    pub fn send_job_response(&mut self, job: &mut JobTemplate, rpcid: String) -> Result<(), String> {
        trace!(LOGGER, "Worker {} - Sending a job response downstream", self.id);
        // Set the difficulty
        job.difficulty = self.status.difficulty;
        self.needs_job = None;
        let job_value = serde_json::to_value(job).unwrap();
        return self.protocol.send_response(
            &mut self.stream,
            "getjobtemplate".to_string(),
            job_value,
            rpcid,
        );
    }

    /// Send worker mining status
    pub fn send_status(&mut self, status: WorkerStatus, rpcid: String) -> Result<(), String> {
        trace!(LOGGER, "Worker {} - Sending worker status", self.id);
        let status_value = serde_json::to_value(status).unwrap();
        return self.protocol.send_response(
            &mut self.stream,
            "status".to_string(),
            status_value,
            rpcid,
        );
    }

    /// Send OK Response
    pub fn send_ok(&mut self, method: String, rpcid: String) -> Result<(), String> {
        trace!(LOGGER, "Worker {} - sending OK Response", self.id);
        return self.protocol.send_response(
            &mut self.stream,
            method,
            serde_json::to_value("ok".to_string()).unwrap(),
            rpcid,
        );
    }

    /// Return any pending shares from this worker
    pub fn get_shares(&mut self) -> Result<Option<Vec<SubmitParams>>, String> {
        if self.shares.len() > 0 {
            trace!(
                LOGGER,
                "Worker {} - Getting {} shares",
                self.id,
                self.shares.len()
            );
            let current_shares = self.shares.clone();
            self.shares = Vec::new();
            return Ok(Some(current_shares));
        }
        return Ok(None);
    }

    /// Get and process messages from the connected worker
    // Method to handle requests from the downstream worker
    pub fn process_messages(&mut self) -> Result<(), String> {
        // XXX TODO: With some reasonable rate limiting (like N message per pass)
        // Read some messages from the upstream
        // Handle each request
        match self.protocol.get_message(&mut self.stream) {
            Ok(rpc_msg) => {
                match rpc_msg {
                    Some(message) => {
                        trace!(LOGGER, "Worker {} - Got Message: {:?}", self.id, message);
                        // let v: Value = serde_json::from_str(&message).unwrap();
                        let req: RpcRequest = match serde_json::from_str(&message) {
                            Ok(r) => r,
                            Err(e) => {
                                self.error = true;
                                // XXX TODO: Invalid request
                                return Err(e.to_string());
                            }
                        };
                        trace!(
                            LOGGER,
                            "Worker {} - Received request type: {}",
                            self.id,
                            req.method
                        );
                        match req.method.as_str() {
                            "login" => {
                                debug!(LOGGER, "Worker {} - Accepting Login request", self.id);
                                let params: Value = match req.params {
                                    Some(p) => p,
                                    None => {
                                        self.error = true;
                                        // XXX TODO: Invalid request
                                        return Err("invalid request".to_string());
                                    }
                                };
                                let login_params: LoginParams = match serde_json::from_value(params)
                                {
                                    Ok(p) => p,
                                    Err(e) => {
                                        self.error = true;
                                        // XXX TODO: Invalid request
                                        return Err(e.to_string());
                                    }
                                };
                                // XXX TODO: Validate the login - is it a valid grin wallet address?
                                self.login = Some(login_params);
                                // We accepted the login, send ok result
                                self.send_ok(req.method, req.id);
                            }
                            "getjobtemplate" => {
                                debug!(LOGGER, "Worker {} - Accepting request for job", self.id);
                                self.needs_job = req.id.clone();
                            }
                            "submit" => {
                                debug!(LOGGER, "Worker {} - Accepting share", self.id);
                                match serde_json::from_value(req.params.unwrap()) {
					Result::Ok(share) => {
                           			self.shares.push(share);
					},
					Result::Err(err) => { }
				};
					
                            }
                            "status" => {
                                trace!(LOGGER, "Worker {} - Accepting status request", self.id);
                                let status = self.status.clone();
                                self.send_status(status, req.id);
                            }
                            "keepalive" => {
                                trace!(LOGGER, "Worker {} - Accepting keepalive request", self.id);
                                self.send_ok(req.method, req.id);
                            }
                            _ => {
                                warn!(
                                    LOGGER,
                                    "Worker {} - Unknown request: {}",
                                    self.id,
                                    req.method.as_str()
                                );
                                self.error = true;
                                return Err("Unknown request".to_string());
                            }
                        };
                    }
                    None => {} // Not an error, just no messages for us right now
                }
            }
            Err(e) => {
                self.error = true;
                return Err(e.to_string());
            }
        }
        return Ok(());
    }
}
