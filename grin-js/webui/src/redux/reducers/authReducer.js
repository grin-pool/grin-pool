// @flow

import { combineReducers } from 'redux'
import type { Account, Reducer, Action } from '../../types.js'

export type AuthState = {
  account: Account | null,
  isCreatingAccount: boolean,
  isLoggingIn: boolean,
  authError: string
}

export type AccountAction = { type: 'ACCOUNT', data: Account }

export const account = (state: Account | null = null, action: AccountAction): Account | null => {
  switch (action.type) {
    case 'ACCOUNT':
      return action.data
    default:
      return state
  }
}

export type IsCreatingAccountAction = { type: string, data?: boolean}

export const isCreatingAccount = (state: boolean = false, action: IsCreatingAccountAction): ?boolean => {
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

export type IsLoggingInAction = { type: string, data?: boolean }

export const isLoggingIn = (state: boolean = false, action: IsLoggingInAction): ?boolean => {
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

export type AuthErrorAction = {
  type: 'AUTH_ERROR', data: { authError: string }
} | {
  type: 'IS_LOGGING_IN', data?: boolean
} | {
  type: 'IS_CREATING_ACCOUNT', data?: boolean
}

const authError = (state: string = '', action: AuthErrorAction): string => {
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

export const auth: Reducer<AuthState, Action> = combineReducers({
  account,
  isCreatingAccount,
  isLoggingIn,
  authError
})
