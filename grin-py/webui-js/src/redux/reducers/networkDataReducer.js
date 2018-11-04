import { combineReducers } from 'redux'

export const historical = (state = [], action) => {
  switch (action.type) {
    case 'NETWORK_DATA':
      return action.data.historical
    default:
      return state
  }
}

export const latestBlock = (state = {}, action) => {
  switch (action.type) {
    case 'NETWORK_DATA':
      return action.data.latestBlock
    default:
      return state
  }
}

export const networkData = combineReducers({
  historical,
  latestBlock
})
