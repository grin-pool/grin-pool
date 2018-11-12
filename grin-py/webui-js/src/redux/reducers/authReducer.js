import { combineReducers } from 'redux'

export const account = (state = null, action) => {
  switch (action.type) {
    case 'ACCOUNT':
      return action.data
    default:
      return state
  }
}

export const auth = combineReducers({
  account
})
