export interface DatabaseGrinBlock {
    height: number,
    hash: string,
    version: number,
    previous: string,
    timestamp: any,
    output_root: string,
    range_proof_root: string,
    kernel_root: string,
    nonce: string,
    edge_bits: number,
    total_difficulty: number,
    secondary: number,
    num_inputs: number,
    num_outputs: number,
    num_kernels: number,
    fee: number,
    lock_height: number,
    total_kernel_offset: string,
    state: string,
    secondary_scaling: number
}

export interface DatabaseGrinStat {
    difficulty: number,
    gps: number,
    edge_bits: number,
    height: number,
    timestamp: number,
    secondary_scaling: number
}

export interface DatabasePoolBlock {
    height: number,
    hash: string,
    nonce: number,
    actual_difficulty: number,
    net_difficulty: number,
    timestamp: any,
    state: string,
    found_by: number
}

export interface DatabasePoolStat {
    height: number,
    timestamp: number,
    active_miners: number,
    shares_processed: number,
    total_blocks_found: number,
    total_shares_processed: number,
    dirty: number,
    share_counts: string,
    id: number,
    edge_bits: number,
    gps: number,
    grin_stats_id: null | number,
    pool_stats_id: null | number,
    worker_stats_id: null | number
}

export type MergeBlocksInput = DatabaseGrinStat | BlockGpsStat | DatabasePoolStat | WorkerGpsStat

export interface GPS {
    edge_bits: number,
    gps: number
}

export interface BlockGpsStat {
    id: number,
    timestamp: number,
    height: number,
    valid_shares: number,
    invalid_shares: number,
    stale_shares: number,
    total_valid_shares: number,
    total_invalid_shares: number,
    total_stale_shares: number,
    dirty: number,
    user_id: number,
    edge_bits: number,
    gps: number,
    grin_stats_id: null | number,
    pool_stats_id: null | number,
    worker_stats_id: number
}

export interface MergedBlockGpsStat {
    id: number,
    timestamp: number,
    height: number,
    valid_shares: number,
    invalid_shares: number,
    stale_shares: number,
    total_valid_shares: number,
    total_invalid_shares: number,
    total_stale_shares: number,
    dirty: number,
    user_id: number,
    gps: GPS[],
    grin_stats_id: null | number,
    pool_stats_id: null | number,
    worker_stats_id: number
}

export interface WorkerShareStat {
    id: number,
    edge_bits: number,
    share_edge_bits: number,
    difficulty: number,
    valid: number,
    invalid: number,
    stale: number,
    parent_id: number,
    height: number,
    timestamp: any,
    user_id: number,
    hash: string,
    version: number,
    previous: string,
    output_root: string,
    range_proof_root: string,
    kernel_root: string,
    nonce: string,
    total_difficulty: number,
    secondary_scaling: number,
    num_inputs: number,
    num_outputs: number,
    num_kernels: number,
    fee: number,
    lock_height: number,
    total_kernel_offset: string,
    state: string
}

export interface WorkerGpsStat {
    id: number,
    timestamp: number,
    height: number,
    valid_shares: number,
    invalid_shares: number,
    stale_shares: number,
    total_valid_shares: number,
    total_invalid_shares: number,
    total_stale_shares: number,
    dirty: number,
    user_id: number,
    edge_bits: number,
    gps: number,
    grin_stats_id: null | number,
    pool_stats_id: null | number,
    worker_stats_id: number
}

export interface PoolStat {
    height: number,
    timestamp: any,
    active_miners: number,
    shares_processed: number,
    total_blocks_found: number,
    total_shares_processed: number,
    dirty: number,
    share_counts: string,
    hash: string,
    version: number,
    previous: string,
    output_root: string,
    range_proof_root: string,
    kernel_root: string,
    nonce: string,
    edge_bits: number,
    total_difficulty: number,
    secondary_scaling: number,
    num_inputs: number,
    num_outputs: number,
    num_kernels: number,
    fee: number,
    lock_height: number,
    total_kernel_offset: string,
    state: string
}

export interface FindUserResult {
    id: number,
    username: string,
    password_hash: string,
    email: string,
    settings: string,
    extra1: string
  }

  export interface PoolStats {
    height: number,
    timestamp: any,
    active_miners: number,
    shares_processed: number,
    total_blocks_found: number,
    total_shares_processed: number,
    dirty: number,
    share_counts: string,
    hash: string,
    version: number,
    previous: string,
    output_root: string,
    range_proof_root: string,
    kernel_root: string,
    nonce: string,
    edge_bits: number,
    total_difficulty: number,
    secondary_scaling: number,
    num_inputs: number,
    num_outputs: number,
    num_kernels: number,
    fee: number,
    lock_height: number,
    total_kernel_offset: string,
    state: string
  }

  export interface DatabaseWorkerStat {
    id: number,
    timestamp: any,
    height: number,
    valid_shares: number,
    invalid_shares: number,
    stale_shres: number,
    total_valid_shares: number,
    total_invalid_shares: number,
    total_stale_shares: number,
    dirty: number,
    user_id: number
  }

  export interface BlockAlgoValidShare {
    edge_bits: number,
    valid: number,
    height: number
  }

  export interface DatabasePoolUtxo {
    id: number,
    address: null,
    method: null,
    locked: number,
    amount: number,
    failure_count: number,
    last: any,
    last_success: any,
    total_amount: number,
    user_id: number
  }

  export interface DatabasePoolPayment {
    id: number,
    timestamp: any,
    height: number,
    address: string,
    amount: number,
    method: string,
    fee: number,
    failure_count: number,
    invoked: string,
    state: string,
    tx_data: string,
    user_id: number
  }

export interface DatabaseWorkerShares {
    id: number,
    height: number,
    timestamp: any,
    user_id: number,
    share_edge_bits: number
}

export interface DatabaseShares {
    id: number,
    edge_bits: number,
    difficulty: number,
    valid: number,
    invalid: number,
    stale: number,
    parent_id: number
}

  export type PoolSharesQueryResult = DatabaseGrinBlock & DatabasePoolStat

  export type UserSharesQueryResult = DatabaseWorkerShares & DatabaseGrinBlock & DatabaseShares