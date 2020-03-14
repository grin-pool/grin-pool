// @flow

import { combineReducers } from 'redux'
import { type Action } from '../../types.js'
export const historical = (state: Array<Object> = [], action: Action) => {
  switch (action.type) {
    case 'NETWORK_DATA':
      return action.data.historical
    default:
      return state
  }
}

export const blocksByHeight = (state: { [number]: number } = {}, action: Action) => {
  switch (action.type) {
    case 'NETWORK_DATA':
      return action.data.blocksByHeight
    default:
      return state
  }
}

export const recentBlocks = (state: Array<Object> = [], action: Action) => {
  switch (action.type) {
    case 'NETWORK_RECENT_BLOCKS':
      return action.data
    default:
      return state
  }
}

export const minedBlockAlgos = (state: any = { c29: [], c31: [] }, action: Action) => {
  switch (action.type) {
    case 'MINED_BLOCKS_ALGOS':
      return action.data
    default:
      return state
  }
}

export const latestBlock = (state: Object = {}, action: Action) => {
  switch (action.type) {
    case 'LATEST_BLOCK':
      return action.data.latestBlock
    default:
      return state
  }
}

export const networkData = combineReducers({
  historical,
  blocksByHeight,
  recentBlocks,
  minedBlockAlgos,
  latestBlock
})
