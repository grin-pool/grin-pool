import { combineReducers } from 'redux'

export const historical = (state = [], action) => {
  switch (action.type) {
    case 'GRIN_POOL_DATA':
      return action.data.historical
    default:
      return state
  }
}

export const grinPoolData = combineReducers({
  historical
})
