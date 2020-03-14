import { Dispatch as ReduxDispatch } from 'redux'
export type Action = { type: string, data?: any }

export interface State {

  theme: any,
  sidebar: {
    show: boolean,
    collapse: boolean
  }
}

export type ThunkDispatch<A> = ((Dispatch, GetState) => Promise<void> | void) => A

export type Dispatch = ReduxDispatch<Action> & ThunkDispatch<Action>

export type GetState = () => State

export interface Providers {
  [key: string]: any
}

export type FunctionType = (...args: any[]) => any
export type ActionsCreatorsMapObject = { [actionCreator: string]: FunctionType}

export type CreateUserResponse = {
  id: number,
  token: string
}

export type Account = {
  ...CreateUserResponse,
  username: string
} | null

export type GPS = Array<{ edge_bits: number, gps: number }>

export type ShareTypeCount = {
  state: number,
  valid: number,
  invalid: number
}

export type NetworkBlockData = {
  difficulty: number,
  gps: Array<GPS>,
  height: number,
  timestamp: number,
  secondary_scaling: number
}

export type GrinPoolBlockData = {
  height: number,
  timestamp: number,
  active_miners: number,
  shares_processed: number,
  total_blocks_found: number,
  total_shares_processed: number,
  dirty: number,
  share_counts: { C29: ShareTypeCount, C31: ShareTypeCount },
  id: number,
  gps: Array<GPS>
}

export type MinerBlockData = {
  dirty: number,
  gps: GPS,
  height: number,
  valid_shares: number,
  invalid_shares: number,
  stale_shares: number,
  timestamp: number,
  total_invalid_shares: number,
  total_stale_shares: number,
  total_valid_shares: number
}

export type MinerPoolCreditStat = {
  height: number,
  minerC29: number,
  minerC31: number,
  poolC29: number,
  poolC31: number,
  secondary_scaling: number
}

export type MinerAlgoShareCount = {
  c29ValidShares: number, height: number
} | {
  c31ValidShares: number, height: number
} | {
  c29ValidShares: number, height: number,
  c31ValidShares: number, height: number
}

export type MinerShareData = {
  [string]: MinerAlgoShareCount
}

export type PoolSharesSubmitted = {
  height: number,
  timestamp: number,
  active_miners: number,
  shares_processed: number,
  total_blocks_found: number,
  total_shares_processed: number,
  dirty: number,
  share_counts: string,
  gps: Array<GPS>,

}
