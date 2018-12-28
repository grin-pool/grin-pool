use std::collections::HashMap;
use std::io;
use std::ops::Deref;
use std::str::FromStr;
use std::time::Duration;

use pool::config::{Config, ProducerConfig};
use pool::logger::LOGGER;
use pool::proto::SubmitParams;

use kafka::client::{
    Compression, KafkaClient, RequiredAcks, DEFAULT_CONNECTION_IDLE_TIMEOUT_MILLIS,
};
use kafka::producer::{AsBytes, Producer, Record, DEFAULT_ACK_TIMEOUT_MILLIS};

pub struct Share {
    height: u64,
    job_id: u64,
    nonce: u64,
    server_id: String,
    worker_id: usize,
    worker_addr: String,
    message: String,
}

impl Share {
    pub fn new(height: u64, job_id: u64, nonce: u64, server_id: String, worker_id: usize, worker_addr: String) -> Share {
        Share {
            height: height,
            job_id: job_id,
            nonce: nonce,
            server_id: server_id.clone(),
            worker_addr: worker_addr.clone(),
            worker_id: worker_id,
            message: format!(
                "share(jobId: {}, ip: {}, sserver: {}, height: {}, userId: {})",
                job_id, worker_addr, server_id, height, worker_id
            ),
        }
    }
}

impl AsBytes for Share {
    fn as_bytes(&self) -> &[u8] {
        self.message.as_bytes()
    }
}

pub struct KafkaProducer {
    pub topic: String,
    pub client: Producer,
    pub partitions: i32,
}

struct KafkaProducerConfig {
    compression: Compression,
    required_acks: RequiredAcks,
    batch_size: usize,
    conn_idle_timeout: Duration,
    ack_timeout: Duration,
}

impl KafkaProducerConfig {
    fn new(
        _compression: Option<&String>,
        _required_acks: Option<&String>,
        _batch_size: Option<&String>,
        _conn_idle_timeout: Option<&String>,
        _ack_timeout: Option<&String>,
    ) -> KafkaProducerConfig {
        KafkaProducerConfig {
            compression: match _compression {
                None => Compression::NONE,
                Some(ref s) if s.eq_ignore_ascii_case("none") => Compression::NONE,
                #[cfg(feature = "gzip")]
                Some(ref s) if s.eq_ignore_ascii_case("gzip") => Compression::GZIP,
                #[cfg(feature = "snappy")]
                Some(ref s) if s.eq_ignore_ascii_case("snappy") => Compression::SNAPPY,
                Some(s) => panic!(format!("Unsupported compression type: {}", s)),
            },
            required_acks: match _required_acks {
                None => RequiredAcks::One,
                Some(ref s) if s.eq_ignore_ascii_case("none") => RequiredAcks::None,
                Some(ref s) if s.eq_ignore_ascii_case("one") => RequiredAcks::One,
                Some(ref s) if s.eq_ignore_ascii_case("all") => RequiredAcks::All,
                Some(s) => panic!(format!("Unknown --required-acks argument: {}", s)),
            },
            batch_size: to_number(_batch_size, 1).unwrap(),
            conn_idle_timeout: Duration::from_millis(
                to_number(_conn_idle_timeout, DEFAULT_CONNECTION_IDLE_TIMEOUT_MILLIS).unwrap(),
            ),
            ack_timeout: Duration::from_millis(
                to_number(_ack_timeout, DEFAULT_ACK_TIMEOUT_MILLIS).unwrap(),
            ),
        }
    }
}

impl Default for KafkaProducerConfig {
    fn default() -> KafkaProducerConfig {
        KafkaProducerConfig::new(
            None, // Compression NONE
            None, // RequiredAcks One
            None, // batch_size 1
            None, // conn_idle_timeout DEFAULT_CONNECTION_IDLE_TIMEOUT_MILLIS
            None, // ack_timeout DEFAULT_ACK_TIMEOUT_MILLIS
        )
    }
}

fn to_number<N: FromStr>(s: Option<&String>, _default: N) -> Result<N> {
    match s {
        None => Ok(_default),
        Some(s) => match s.parse::<N>() {
            Ok(n) => Ok(n),
            Err(_) => Ok(_default),
        },
    }
}

pub trait GrinProducer {
    fn from_config(config: &ProducerConfig) -> KafkaProducer;

    fn send_data(&mut self, share: Share) -> Result<()>;
}

impl GrinProducer for KafkaProducer {
    fn from_config(cfg: &ProducerConfig) -> KafkaProducer {
        let client = KafkaClient::new(cfg.brokers.clone());
        let producer = {
            let options: Option<HashMap<String, String>> = cfg.options.clone();
            let kafka_config: KafkaProducerConfig;
            if options.is_some() {
                let options = options.unwrap();
                kafka_config = KafkaProducerConfig::new(
                    options.get("compression"),
                    options.get("required_acks"),
                    options.get("batch_size"),
                    options.get("conn_idle_timeout"),
                    options.get("ack_timeout"),
                );
            } else {
                kafka_config = KafkaProducerConfig::default();
            }
            Producer::from_client(client)
                .with_ack_timeout(kafka_config.ack_timeout)
                .with_required_acks(kafka_config.required_acks)
                .with_compression(kafka_config.compression)
                .with_connection_idle_timeout(kafka_config.conn_idle_timeout)
                .create()
                .unwrap()
        };

        KafkaProducer {
            topic: cfg.topic.clone(),
            partitions: cfg.partitions,
            client: producer,
        }
    }

    fn send_data(&mut self, share: Share) -> Result<()> {
        let record = Record::from_value(&self.topic, share).with_partition(self.partitions);
        self.client.send(&record)?;
        Ok(())
    }
}

error_chain! {
    links {
        Kafka(kafka::error::Error, kafka::error::ErrorKind);
    }
    foreign_links {
        Io(io::Error);
    }
}
