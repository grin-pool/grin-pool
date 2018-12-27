// @flow

import { combineReducers } from 'redux'

const historical = (state: Array<any> = [], action) => {
  switch (action.type) {
    case 'MINER_DATA':
      return action.data.historical
    default:
      return state
  }
}

const totalSharesSubmitted = (state: number = 0, action) => {
  switch (action.type) {
    case 'MINER_TOAL_VALID_SHARES':
      return action.data.totalSharesSubmitted
    default:
      return state
  }
}

const paymentData = (state: Object = {}, action) => {
  switch (action.type) {
    case 'MINER_PAYMENT_DATA':
      return action.data
    default:
      return state
  }
}

const isPaymentSettingProcessing = (state: boolean = false, action) => {
  switch (action.type) {
    case 'IS_PAYMENT_SETTING_PROCESSING':
      return action.data
    case 'UPDATE_PAYMENT_METHOD_SETTING':
      return false
    case 'MANUAL_PAYMENT_SUBMISSION':
      return false
    default:
      return state
  }
}

const minerPaymentTxSlate = (state: string = '', action) => {
  switch (action.type) {
    case 'MINER_PAYMENT_TX_SLATE':
      return action.data
    default:
      return state
  }
}

const isTxSlateLoading = (state: boolean = false, action) => {
  switch (action.type) {
    case 'IS_TX_SLATE_LOADING':
      return action.data
    default:
      return state
  }
}

const payoutScript = (state: string = '', action) => {
  switch (action.type) {
    case 'PAYOUT_SCRIPT':
      return action.data
    default:
      return state
  }
}

const paymentFormFeedback = (state: null | string = null, action) => {
  switch (action.type) {
    case 'PAYMENT_FORM_FEEDBACK':
      return action.data
    case 'IS_PAYMENT_SETTING_PROCESSING':
      if (!action.data) {
        return {
          message: 'There has been an issue with your submission. Please try again later.',
          color: 'danger'
        }
      }
      return ''
    case 'UPDATE_PAYMENT_METHOD_SETTING':
      return {
        message: 'Payment setting successfully saved!',
        color: 'success'
      }
    case 'MANUAL_PAYMENT_SUBMISSION':
      if (action.data) {
        return {
          color: 'success',
          message: 'Payment submitted successfully, please allow a few minutes for transaction to show in wallet.'
        }
      }
      return {
        color: 'danger',
        message: 'Payment failed, please check URL / username and try again'
      }
    default:
      return state
  }
}

export const latestMinerPayments = (state: Array<Object> = [], action) => {
  switch (action.type) {
    case 'LATEST_MINER_PAYMENTS':
      return action.data
    default:
      return state
  }
}

export const minerData = combineReducers({
  historical,
  totalSharesSubmitted,
  paymentData,
  latestMinerPayments,
  minerPaymentTxSlate,
  isPaymentSettingProcessing,
  isTxSlateLoading,
  payoutScript,
  paymentFormFeedback
})
