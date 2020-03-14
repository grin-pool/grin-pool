// @flow

import { combineReducers } from 'redux'
import type { Reducer, Action } from '../../types'

type MinerDataState = {
  historical: Array<any>,
  totalSharesSubmitted: number,
  minerShareData: Object,
  rigGpsData: Object,
  paymentData: Object,
  minerImmatureBalance: number,
  latestBlockGrinEarned: number,
  isPaymentSettingProcessing: boolean,
  minerPaymentTxSlate: string,
  isTxSlateLoading: boolean,
  payoutScript: string,
  paymentFormFeedback: null | string,
  latestMinerPayments: Array<Object>,
  totalPayoutsAmount: number,
  isAudioEnabled: boolean,
}

type MinerHistoricalBlockAction = { type: 'MINER_DATA', data: { historical: Array<any> }} | { type: 'ACCOUNT', data: null }

const historical = (state: Array<any> = [], action: MinerHistoricalBlockAction) => {
  switch (action.type) {
    case 'MINER_DATA':
      return action.data.historical
    case 'ACCOUNT':
      if (action.data === null) {
        return []
      }
      return state
    default:
      return state
  }
}

const rigGpsData = (state: any = { c29: [], c31: [] }, action: any) => {
  switch (action.type) {
    case 'RIG_DATA':
      return action.data.rigGpsData
    default:
      return state
  }
}

const rigShareData = (state: any = {}, action: any) => {
  switch (action.type) {
    case 'RIG_DATA':
      return action.data.rigShareData || {}
    default:
      return state
  }
}

const rigWorkers = (state: Array<string> = [], action: any) => {
  switch (action.type) {
    case 'RIG_DATA':
      return action.data.rigWorkers
    default:
      return state
  }
}

type MinerTotalValidSharesAction = { type: 'MINER_TOTAL_VALID_SHARES', data: { totalSharesSubmitted: number } } | { type: 'ACCOUNT', data: null }

const totalSharesSubmitted = (state: number = 0, action: MinerTotalValidSharesAction) => {
  switch (action.type) {
    case 'MINER_TOTAL_VALID_SHARES':
      return action.data.totalSharesSubmitted
    case 'ACCOUNT':
      if (action.data === null) {
        return 0
      }
      return state
    default:
      return state
  }
}

type MinerShareDataAction = { type: 'MINER_SHARE_DATA', data: { minerShareData: Object } } | { type: 'ACCOUNT', data: null }

const minerShareData = (state: Object = {}, action: MinerShareDataAction) => {
  switch (action.type) {
    case 'MINER_SHARE_DATA':
      return action.data.minerShareData
    case 'ACCOUNT':
      if (action.data === null) {
        return {}
      }
      return state
    default:
      return state
  }
}

type MinerPaymentDataAction = { type: 'MINER_PAYMENT_DATA', data: Object } | { type: 'ACCOUNT', data: null }

const paymentData = (state: Object = {}, action: MinerPaymentDataAction) => {
  switch (action.type) {
    case 'MINER_PAYMENT_DATA':
      return action.data
    case 'ACCOUNT':
      if (action.data === null) {
        return {}
      }
      return state
    default:
      return state
  }
}

type MinerImmatureBalanceAction = { type: 'MINER_IMMATURE_BALANCE', data: number} | { type: 'ACCOUNT', data: null }

const minerImmatureBalance = (state: number = 0, action: MinerImmatureBalanceAction) => {
  switch (action.type) {
    case 'MINER_IMMATURE_BALANCE':
      return action.data
    case 'ACCOUNT':
      if (action.data === null) {
        return 0
      }
      return state
    default:
      return state
  }
}

type LatestBlockGrinEarnedAction = { type: 'MINER_LATEST_BLOCK_GRIN_EARNED', data: number } | { type: 'ACCOUNT', data: null }

const latestBlockGrinEarned = (state: number = 0, action: LatestBlockGrinEarnedAction) => {
  switch (action.type) {
    case 'MINER_LATEST_BLOCK_GRIN_EARNED':
      return action.data
    case 'ACCOUNT':
      if (action.data === null) {
        return 0
      }
      return state
    default:
      return state
  }
}

type NextBlockGrinEarnedAction = { type: 'MINER_Next_BLOCK_GRIN_EARNED', data: number } | { type: 'ACCOUNT', data: null }

const nextBlockGrinEarned = (state: number = 0, action: NextBlockGrinEarnedAction) => {
  switch (action.type) {
    case 'MINER_NEXT_BLOCK_GRIN_EARNED':
      return action.data
    case 'ACCOUNT':
      if (action.data === null) {
        return 0
      }
      return state
    default:
      return state
  }
}

type IsPaymentSettingProcessingAction = {
  type: 'IS_PAYMENT_SETTING_PROCESSING' | 'UPDATE_PAYMENT_METHOD_SETTING' | 'MANUAL_PAYMENT_SUBMISSION' | 'MANUAL_PAYMENT_FAILURE',
  data?: boolean
} | { type: 'ACCOUNT', data: null }

const isPaymentSettingProcessing = (state: boolean = false, action: IsPaymentSettingProcessingAction) => {
  switch (action.type) {
    case 'IS_PAYMENT_SETTING_PROCESSING':
      return action.data
    case 'UPDATE_PAYMENT_METHOD_SETTING':
      return false
    case 'MANUAL_PAYMENT_SUBMISSION':
      return false
    case 'MANUAL_PAYMENT_FAILURE':
      return false
    case 'ACCOUNT':
      if (action.data === null) {
        return false
      }
      return state
    default:
      return state
  }
}

type MinerPaymentTxSlateAction = { type: 'MINER_PAYMENT_TX_SLATE', data: string } | { type: 'ACCOUNT', data: null }

const minerPaymentTxSlate = (state: string = '', action: MinerPaymentTxSlateAction) => {
  switch (action.type) {
    case 'MINER_PAYMENT_TX_SLATE':
      return action.data
    case 'ACCOUNT':
      if (action.data === null) {
        return ''
      }
      return state
    default:
      return state
  }
}

type IsTxSlateLoadingAction = { type: 'IS_TX_SLATE_LOADING', data: boolean } | { type: 'ACCOUNT', data: null }

const isTxSlateLoading = (state: boolean = false, action: IsTxSlateLoadingAction) => {
  switch (action.type) {
    case 'IS_TX_SLATE_LOADING':
      return action.data
    case 'ACCOUNT':
      if (action.data === null) {
        return false
      }
      return state
    default:
      return state
  }
}

type PayoutScriptAction = { type: 'PAYOUT_SCRIPT', data: string } | { type: 'ACCOUNT', data: null }

const payoutScript = (state: string = '', action: PayoutScriptAction) => {
  switch (action.type) {
    case 'PAYOUT_SCRIPT':
      return action.data
    case 'ACCOUNT':
      if (action.data === null) {
        return ''
      }
      return state
    default:
      return state
  }
}

type PaymentFormFeedbackAction = {
  type: 'PAYMENT_FORM_FEEDBACK' | 'IS_PAYMENT_SETTING_PROCESSING' | 'UPDATE_PAYMENT_METHOD_SETTING'
  | 'MANUAL_PAYMENT_SUBMISSION',
  data: null | string
 } | { type: 'MANUAL_PAYMENT_FAILURE', data: { message: string}} | { type: 'ACCOUNT', data: null }

const paymentFormFeedback = (state: null | string = null, action: PaymentFormFeedbackAction) => {
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
    case 'MANUAL_PAYMENT_FAILURE':
      return {
        message: action.data.message,
        color: 'danger'
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
    case 'ACCOUNT':
      if (action.data === null) {
        return null
      }
      return state
    default:
      return state
  }
}

type LatestMinerPaymentAction = { type: 'LATEST_MINER_PAYMENTS', data: { latestMinerPayments: Array<Object> }} | { type: 'ACCOUNT', data: null }

export const latestMinerPayments = (state: Array<Object> = [], action: LatestMinerPaymentAction) => {
  if (!action.data) return state
  switch (action.type) {
    case 'LATEST_MINER_PAYMENTS':
      return action.data.latestMinerPayments
    case 'ACCOUNT':
      if (action.data === null) {
        return []
      }
      return state
    default:
      return state
  }
}

type TotalPayoutsAmountAction = { type: 'LATEST_MINER_PAYMENTS', data: { totalPayoutsAmount: number }} | { type: 'ACCOUNT', data: null }

export const totalPayoutsAmount = (state: number = 0, action: TotalPayoutsAmountAction) => {
  if (!action.data) return state
  switch (action.type) {
    case 'LATEST_MINER_PAYMENTS':
      return action.data.totalPayoutsAmount
    case 'ACCOUNT':
      if (action.data === null) {
        return 0
      }
      return state
    default:
      return state
  }
}

type IsAudioEnabledAction = { type: 'IS_AUDIO_ENABLED', data: boolean } | { type: 'ACCOUNT', data: null }

export const isAudioEnabled = (state: boolean = false, action: IsAudioEnabledAction) => {
  switch (action.type) {
    case 'IS_AUDIO_ENABLED':
      return !state
    case 'ACCOUNT':
      if (action.data === null) {
        return false
      }
      return state
    default:
      return state
  }
}

export const minerData: Reducer<MinerDataState, Action> = combineReducers({
  historical,
  rigGpsData,
  rigShareData,
  rigWorkers,
  totalSharesSubmitted,
  paymentData,
  minerShareData,
  minerImmatureBalance,
  latestBlockGrinEarned,
  nextBlockGrinEarned,
  latestMinerPayments,
  totalPayoutsAmount,
  minerPaymentTxSlate,
  isPaymentSettingProcessing,
  isTxSlateLoading,
  payoutScript,
  paymentFormFeedback,
  isAudioEnabled
})
