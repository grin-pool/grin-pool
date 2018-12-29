// @flow

import { combineReducers } from 'redux'

export const historical = (state: Array<any> = [], action) => {
  switch (action.type) {
    case 'GRIN_POOL_DATA':
      return action.data.historical
    default:
      return state
  }
}

export const lastBlockMined = (state: number = 0, action) => {
  switch (action.type) {
    case 'GRIN_POOL_LAST_BLOCK_MINED':
      return action.data.lastBlockMined
    default:
      return state
  }
}

export const recentBlocks = (state: Array<Object> = [], action) => {
  switch (action.type) {
    case 'GRIN_POOL_RECENT_BLOCKS':
      return action.data
    default:
      return state
  }
}

export const poolBlocksMined = (state: Array<any> = [], action) => {
  switch (action.type) {
    case 'POOL_BLOCKS_MINED':
      return action.data.blocksFound
    default:
      return state
  }
}

export const poolBlocksOrphaned = (state: Array<any> = [], action) => {
  switch (action.type) {
    case 'POOL_BLOCKS_MINED':
      return action.data.blocksOrphaned
    default:
      return state
  }
}

export const sharesSubmitted = (state: Array<any> = [], action) => {
  switch (action.type) {
    case 'GRIN_POOL_SHARES_SUBMITTED':
      return action.data.sharesSubmittedData
    default:
      return state
  }
}

export const grinPoolData = combineReducers({
  historical,
  lastBlockMined,
  recentBlocks,
  poolBlocksMined,
  poolBlocksOrphaned,
  sharesSubmitted
})
