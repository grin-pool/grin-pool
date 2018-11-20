import { combineReducers } from 'redux'

export const account = (state = null, action) => {
  switch (action.type) {
    case 'ACCOUNT':
      return action.data
    default:
      return state
  }
}

export const isCreatingAccount = (state = false, action) => {
  switch (action.type) {
    case 'IS_CREATING_ACCOUNT':
      return action.data
    case 'ACCOUNT':
      return false
    case 'IS_LOGGING_IN':
      return false
    case 'AUTH_ERROR':
      return false
    default:
      return state
  }
}

export const isLoggingIn = (state = false, action) => {
  switch (action.type) {
    case 'IS_LOGGING_IN':
      return action.data
    case 'ACCOUNT':
      return false
    case 'AUTH_ERROR':
      return false
    default:
      return state
  }
}

const authError = (state = '', action) => {
  switch (action.type) {
    case 'AUTH_ERROR':
      return action.data.authError
    case 'IS_LOGGING_IN':
      if (action.data === true) {
        return ''
      } else {
        return state
      }
    case 'IS_CREATING_ACCOUNT':
      if (action.data === true) {
        return ''
      } else {
        return state
      }
    default:
      return state
  }
}

export const auth = combineReducers({
  account,
  isCreatingAccount,
  isLoggingIn,
  authError
})
