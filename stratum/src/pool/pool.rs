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

use bufstream::BufStream;
use std::collections::HashMap;
use std::net::{Shutdown, SocketAddr, TcpListener, TcpStream};
use std::sync::{Arc, Mutex, RwLock};
use std::time::Instant;
use std::{thread, time};
use rand::Rng;

use pool::config::{Config, NodeConfig, PoolConfig, WorkerConfig};
use pool::logger::LOGGER;
use pool::proto::{JobTemplate, RpcError, SubmitParams};
use pool::server::Server;
use pool::worker::Worker;
use pool::consensus::Proof;

// ----------------------------------------
// Worker Connection Thread Function

// Run in a thread. Adds new connections to the workers list
fn accept_workers(
    stratum_id: String,
    address: String,
    difficulty: u64,
    workers: &mut Arc<Mutex<HashMap<String, Worker>>>,
) {
    let listener = TcpListener::bind(address).expect("Failed to bind to listen address");
    let banned: HashMap<SocketAddr, Instant> = HashMap::new();
    let mut rng = rand::thread_rng();
    // XXX TODO: Call the Redis api to get a list of banned IPs, refresh that list sometimes
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                match stream.peer_addr() {
                    Ok(worker_addr) => {
                        // XXX ALWAYS DO THIS FIRST - Check if this ip is banned and if so, drop it
                        if banned.contains_key(&worker_addr) {
                            let _ = stream.shutdown(Shutdown::Both);
                            continue;
                        }
                        warn!(
                            LOGGER,
                            "Worker Listener - New connection from ip: {}",
                            worker_addr
                        );
                        stream
                            .set_nonblocking(true)
                            .expect("set_nonblocking call failed");
                        let mut worker = Worker::new(0, BufStream::new(stream));
                        worker.set_difficulty(difficulty);
                        let initial_id = rng.gen::<u32>();
                        workers.lock().unwrap().insert(initial_id.to_string(), worker);
                        // The new worker is now added to the workers list
                    }
                    Err(e) => {
                        warn!(
                            LOGGER,
                            "{} - Worker Listener - Error getting wokers ip address: {:?}", stratum_id, e
                        );
                    }
                }
            }
            Err(e) => {
                warn!(
                    LOGGER,
                    "{} - Worker Listener - Error accepting connection: {:?}", stratum_id, e
                );
            }
        }
    }
    // close the socket server
    drop(listener);
}

// ----------------------------------------
// A Grin mining pool

pub struct Pool {
    id: String,
    job: JobTemplate,
    config: Config,
    server: Server,
    workers: Arc<Mutex<HashMap<String, Worker>>>,
    duplicates: HashMap<Vec<u64>, usize>, // pow vector, worker id who first submitted it
}

impl Pool {
    /// Create a new Grin Stratum Pool
    pub fn new(config: Config) -> Pool {
        Pool {
            id: "Grin Pool".to_string(),
            job: JobTemplate::new(),
            config: config.clone(),
            server: Server::new(config.clone()),
            workers: Arc::new(Mutex::new(HashMap::new())),
            duplicates: HashMap::new(),
        }
    }

    /// Run the Pool
    pub fn run(&mut self) {
        // Start a thread for each listen port to accept new worker connections
        for port_difficulty in &self.config.workers.port_difficulty {
            let mut workers_th = self.workers.clone();
            let id_th = self.id.clone();
            let address_th = self.config.workers.listen_address.clone() + ":"
                + &port_difficulty.port.to_string();
            let difficulty_th = port_difficulty.difficulty;
            let _listener_th = thread::spawn(move || {
                accept_workers(id_th, address_th, difficulty_th, &mut workers_th);
            });
        }

        // ------------
        // Main loop
        loop {
            // XXX TODO: Error checking

            // (re)connect if server is not connected or is in error state
            match self.server.connect() {
                Ok(_) => { } // server.connect method also logs in and requests a job
                Err(e) => {
                    error!(
                        LOGGER,
                        "{} - Unable to connect to upstream server: {}", self.id, e
                    );
                    thread::sleep(time::Duration::from_secs(1));
                    continue;
                }
            }

            // check the server for messages and handle them
            let _ = self.process_server_messages();

            // if the server gave us a new block
            let _ = self.accept_new_job();

            // Process messages from the workers
            let _ = self.process_worker_messages();

            // Process worker shares
            let _ = self.process_shares();

            // Send jobs to needy workers
//            if self.server.job.height > 0 {
            let _ = self.send_jobs();
//            }

            // Delete workers in error state
            let _num_active_workers = self.clean_workers();

            thread::sleep(time::Duration::from_millis(10));
        }
    }

    // ------------
    // Pool Methods
    //

    // Process messages from the upstream server
    // Will contain job requests, submit results, status results, etc...
    fn process_server_messages(&mut self) -> Result<(), RpcError> {
        match self.server.process_messages(&mut self.workers) {
            Ok(_) => {
                return Ok(());
            }
            Err(e) => {
                // Log an error
                error!(
                    LOGGER,
                    "{} - Error processing upstream message: {:?}", self.id, e
                );
                // There are also special case(s) where we want to do something for a specific
                // error
                if e.message.contains("Node is syncing") {
                    thread::sleep(time::Duration::from_secs(2));
                }
                return Err(e);
            }
        }
    }

    fn process_worker_messages(&mut self) {
        let mut id_changed: Vec<String> = vec![];
        let mut w_m = self.workers.lock().unwrap();
        for (worker_id, worker) in w_m.iter_mut() {
            let res = worker.process_messages();
            if worker_id != &*worker.full_id() {
                // User id changed - probably because they logged in
                id_changed.push(worker_id.clone());
                error!( LOGGER, "id changed:  full_id {} - {:?}", worker.full_id().clone(), res );
            }
        }
        // Rehash the worker using updated id
        for orig_id in id_changed.iter() {
            let worker_o = w_m.remove(&orig_id.clone());
            match worker_o {
                None => {},
                Some(worker) => {
                    w_m.insert(worker.full_id(), worker);
                }
            }
        }
    }

    fn send_jobs(&mut self) {
        let mut w_m = self.workers.lock().unwrap();
        for (worker_id, worker) in w_m.iter_mut() {
            if worker.needs_job && worker.authenticated {
                warn!( LOGGER, "job to: {} - needs_job: {}, requested_job: {}, authenticated: {}", worker_id, worker.needs_job, worker.requested_job, worker.authenticated );
                // Randomize the nonce
                // XXX TODO (Need to know block header format and deserialize it
                worker.set_difficulty(1); // XXX TODO: this get from config?
                worker.set_height(self.job.height);
                worker.send_job(&mut self.server.job.clone());
            }
        }
    }

    fn accept_new_job(&mut self) {
        // Use the new job
        if self.job.pre_pow != self.server.job.pre_pow {
            debug!(LOGGER, "accept_new_job: {} vs {}", self.job.pre_pow.clone(), self.server.job.pre_pow.clone());
            self.job = self.server.job.clone();
            debug!(LOGGER, "accept_new_job broadcasting: {}", self.job.pre_pow.clone());
            // broadcast it to the workers
            let _ = self.broadcast_job();
            // clear last block duplicates map
            self.duplicates = HashMap::new()
        }
    }

    //
    // Process shares returned by each workers
    fn process_shares(&mut self) {
        let mut w_m = self.workers.lock().unwrap();
        for (worker_id, worker) in w_m.iter_mut() {
            match worker.get_shares().unwrap() {
                None => {}
                Some(shares) => {
                    for share in shares {
                        //  Check for duplicate or add to duplicate map
                        if self.duplicates.contains_key(&share.pow) {
                            debug!(
                                LOGGER,
                                "{} - Rejected duplicate share from worker {} with login {}",
                                self.id,
                                worker.id(),
                                worker.login(),
                            );
                            worker.status.rejected += 1;
                            worker.block_status.rejected += 1;
                            continue; // Dont process this share anymore
                        } else {
                            self.duplicates.insert(share.pow.clone(), worker.id());
                        }
                        // XXX TODO:
                        // Verify the timestamp matches what we sent so we know
                        //   this share comes from the job we sent
                        // XXX TO DO This I need to deserialize the block header
                        //			if share.pre_pow != self.current_block {
                        //			    debug!(
                        //                                LOGGER,
                        //                                "{} - Rejected corrupt share from worker {} with login {}",
                        //                                self.id,
                        //                                worker.id(),
                        //                                worker.login(),
                        //                            );
                        //                            worker.status.rejected += 1;
                        //                            worker.block_status.rejected += 1;
                        //                            continue; // Dont process this share anymore
                        //                        }
                        // Check the height to see if its stale
                        if share.height != self.job.height {
                            // Its stale
                            warn!(LOGGER, "Share is stale {} vs {}", share.height, self.job.height);
                            worker.status.stale += 1;
                            worker.block_status.stale += 1;
                            worker.send_err("submit".to_string(), "Solution submitted too late".to_string(), -32503);
                            continue; // Dont process this share anymore
                        }
                        // We check the difficulty here
                        let proof = Proof {
                            edge_bits: share.edge_bits as u8,
                            nonces: share.pow.clone().to_vec(),
                        };
                        let difficulty = proof.to_difficulty_unscaled().to_num();
                        warn!(LOGGER, "Difficulty: {}", difficulty);
                        // Check if this meets worker difficulty
                        if difficulty < 1 {
                            worker.status.rejected += 1;
                            worker.block_status.rejected += 1;
                            worker.send_err("submit".to_string(), "Rejected low difficulty solution".to_string(), -32502);
                            continue; // Dont process this share anymore
                        }
                        if difficulty < worker.status.difficulty {
                            worker.status.rejected += 1;
                            worker.block_status.rejected += 1;
                            worker.send_err("submit".to_string(), "Failed to validate solution".to_string(), -32502);
                            continue; // Dont process this share anymore
                        }
                        if difficulty >= worker.status.difficulty {
                            worker.status.accepted += 1;
                            worker.block_status.accepted += 1;
                            worker.send_ok("submit".to_string());
                        }
                        // This is a good share, send it to grin server to be submitted
                        // XXX TODO: Only send high power shares
                        let message_id: String = format!("{}-{}", worker.id(), worker.rig_id());
                        self.server.submit_share(&share.clone(), message_id.clone());
                        warn!(LOGGER, "{} - Got share at height {} with nonce {} with difficulty {} from worker {}",
                                self.id,
                                share.height,
                                share.nonce,
                                worker.status.difficulty,
                                message_id,
                        );
                    }
                }
            }
        }
    }

    fn broadcast_job(&mut self) -> Result<(), String> {
        let mut w_m = self.workers.lock().unwrap();
        debug!(
            LOGGER,
            "{} - broadcasting a job to {} workers",
            self.id,
            w_m.len(),
        );
        // XXX TODO: To do this I need to deserialize the block header
        // XXX TODO: need to randomize the nonce (just in case a miner forgets)
        // XXX TODO: need to set a unique timestamp and record it in the worker struct
        for (worker_id, worker) in w_m.iter_mut() {
            if worker.authenticated {
                worker.set_difficulty(1); // XXX TODO: this get from config?
                worker.set_height(self.job.height);
                worker.send_job(&mut self.job.clone());
            }
        }
        return Ok(());
    }

    // Purge dead/sick workers - remove all workers marked in error state
    fn clean_workers(&mut self) -> usize {
        let mut dead_workers: Vec<String> = vec![];
        let mut w_m = self.workers.lock().unwrap();
        for (worker_id, worker) in w_m.iter_mut() {
            if worker.error() == true {
                warn!(
                    LOGGER,
                    "{} - Dropping worker: {}-{}",
                    self.id,
                    worker.id(),
                    worker.rig_id(),
                );
                dead_workers.push(worker_id.clone());
            }
        }
        // Remove the dead workers
        for worker_id in dead_workers {
            let _ = w_m.remove(&worker_id);
        }
        return w_m.len();
    }

}
