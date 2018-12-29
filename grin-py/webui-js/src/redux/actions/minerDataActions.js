// @flow
import { API_URL } from '../../config.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import { basicAuth } from '../../utils/utils.js'
import { type Dispatch, type GetState } from '../types.js'

export const fetchMinerData = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}worker/stats/${id}/${latestBlockHeight},${BLOCK_RANGE}/gps,height,valid_shares,timestamp`
    const minerDataResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    const minerData = await minerDataResponse.json()
    dispatch({ type: 'MINER_DATA', data: { historical: minerData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchMinerShares = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/stat/${id}/total_valid_shares`
    const minerSharesResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    const minerShares = await minerSharesResponse.json()
    dispatch({ type: 'MINER_TOAL_VALID_SHARES', data: { totalSharesSubmitted: minerShares.total_valid_shares } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchMinerPaymentData = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/utxo/${id}`
    const minerPaymentResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    const minerPaymentData = await minerPaymentResponse.json()
    if (minerPaymentData) {
      dispatch({ type: 'MINER_PAYMENT_DATA', data: minerPaymentData })
    }
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const getLatestMinerPayments = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/payment/${id}`
    const latestMinerPaymentResponse = await fetch(url, {
      headers: {
        authorization: basicAuth(state.auth.account.token)
      }
    })
    const latestMinerPaymentData = await latestMinerPaymentResponse.json()
    console.log('latestMinerPaymentData: ', latestMinerPaymentData)
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const getLatestMinerPaymentRange = (range?: number = 20) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/payments/${id}/${range}`
    const latestMinerPaymentResponse = await fetch(url, {
      headers: {
        authorization: basicAuth(state.auth.account.token)
      }
    })
    const latestMinerPaymentData = await latestMinerPaymentResponse.json()
    console.log('latestMinerPaymentData: ', latestMinerPaymentData)
    dispatch({
      type: 'LATEST_MINER_PAYMENTS',
      data: latestMinerPaymentData
    })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchMinerPaymentTxSlate = () => async (dispatch: Dispatch, getState: GetState) => {
  dispatch({
    type: 'IS_TX_SLATE_LOADING',
    data: true
  })
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}pool/payment/get_tx_slate/${id}`
    const minerPaymentTxSlateResponse = await fetch(url, {
      method: 'POST',
      headers: {
        authorization: basicAuth(state.auth.account.token)
      }
    })
    const minerPaymentTxSlateData = await minerPaymentTxSlateResponse.json()
    dispatch({
      type: 'MINER_PAYMENT_TX_SLATE',
      data: JSON.stringify(minerPaymentTxSlateData)
    })
  } catch (e) {
    console.log('Error: ', e)
  }
  dispatch({
    type: 'IS_TX_SLATE_LOADING',
    data: false
  })
}

export const setPaymentMethodSetting = (formState: any) => async (dispatch: Dispatch, getState: GetState) => {
  dispatch({
    type: 'IS_PAYMENT_SETTING_PROCESSING',
    data: true
  })
  try {
    const state = getState()
    const id = state.auth.account.id
    const authorizedPost = {
      method: 'POST',
      headers: {
        authorization: basicAuth(state.auth.account.token)
      }
    }
    // need to discern between automated payments and manual
    if (formState.paymentType === 'manual') {
      const method = formState.paymentMethod
      const url = `${API_URL}pool/payment/${method}/${id}/${formState.recipient}`
      const requestPaymentResponse = await fetch(url, authorizedPost)
      const requestPaymentData = await requestPaymentResponse.json()
      const isSuccessful = requestPaymentData === 'ok'
      dispatch({
        type: 'MANUAL_PAYMENT_SUBMISSION',
        data: isSuccessful
      })
    } else { // if they are saving a setting
      const methodUrl = `${API_URL}worker/utxo/${id}/method/${formState.paymentMethod}`
      const setPaymentMethodResponse = await fetch(methodUrl, authorizedPost)
      const setPaymentMethodData = await setPaymentMethodResponse.json()
      if (setPaymentMethodData.method !== formState.paymentMethod) throw new Error('Settings save failed!')
      const addressUrl = `${API_URL}worker/utxo/${id}/address/${formState.recipient}`
      const setPaymentSettingResponse = await fetch(addressUrl, authorizedPost)
      const setPaymentSettingData = await setPaymentSettingResponse.json()
      if (setPaymentSettingData.address !== formState.recipient) throw new Error('Settings save failed')
      dispatch({
        type: 'UPDATE_PAYMENT_METHOD_SETTING'
      })
    }
  } catch (e) {
    console.log('Error: ', e)
    dispatch({
      type: 'IS_PAYMENT_SETTING_PROCESSING',
      data: false
    })
  }
}

export const fetchMinerPaymentScript = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}pool/payment/payout_script/${id}`
    const fetchMinerPaymentScriptResponse = await fetch(url, {
      method: 'POST',
      headers: {
        authorization: basicAuth(state.auth.account.token)
      }
    })
    const fetchMinerPaymentScriptData = await fetchMinerPaymentScriptResponse.text()
    dispatch({
      type: 'PAYOUT_SCRIPT',
      data: fetchMinerPaymentScriptData
    })
  } catch (e) {
    console.log('fetchMinerPaymentScript error: ', e)
  }
}
