import { combineReducers } from 'redux'

export const historical = (state = [], action) => {
  switch (action.type) {
    case 'MINER_DATA':
      return action.data.historical
    default:
      return state
  }
}

export const totalSharesSubmitted = (state = 0, action) => {
  switch (action.type) {
    case 'MINER_TOAL_VALID_SHARES':
      return action.data.totalSharesSubmitted
    default:
      return state
  }
}

export const minerData = combineReducers({
  historical,
  totalSharesSubmitted
})
