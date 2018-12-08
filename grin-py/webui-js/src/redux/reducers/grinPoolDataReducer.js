import { combineReducers } from 'redux'

export const historical = (state = [], action) => {
  switch (action.type) {
    case 'GRIN_POOL_DATA':
      return action.data.historical
    default:
      return state
  }
}

export const sharesSubmitted = (state = [], action) => {
  switch (action.type) {
    case 'GRIN_POOL_SHARES_SUBMITTED':
      return action.data.sharesSubmittedData
    default:
      return state
  }
}

export const lastBlockMined = (state = 0, action) => {
  switch (action.type) {
    case 'GRIN_POOL_LAST_BLOCK_MINED':
      return action.data.lastBlockMined
    default:
      return state
  }
}

export const grinPoolData = combineReducers({
  historical,
  lastBlockMined,
  sharesSubmitted
})
