// @flow
import { API_URL, API_URL_V2 } from '../../config.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import { basicAuth, basicAuthLegacy } from '../../utils/utils.js'
import { type Dispatch, type GetState } from '../../types.js'

// complete
export const fetchMinerData = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const previousData = state.minerData.historical
    let previousMaxBlockHeight = latestBlockHeight - BLOCK_RANGE
    previousData.forEach(block => {
      if (block.height > previousMaxBlockHeight) previousMaxBlockHeight = block.height
    })
    const blockDifference = latestBlockHeight - previousMaxBlockHeight
    const url = `${API_URL_V2}worker/stats/${id}/${latestBlockHeight},${blockDifference}/gps,height,valid_shares,timestamp,invalid_shares,stale_shares,edge_bits`
    const basicAuthString = basicAuth(state.auth.account.token)
    const newMinerDataResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuthString
      }
    })
    if (!newMinerDataResponse.ok) return
    const newMinerData = await newMinerDataResponse.json()
    const concatenatedMinerData = [...previousData, ...newMinerData]
    const numberToRemove = concatenatedMinerData.length > BLOCK_RANGE ? concatenatedMinerData.length - BLOCK_RANGE : 0
    const newHistoricalData = concatenatedMinerData.slice(numberToRemove)
    dispatch({ type: 'MINER_DATA', data: { historical: newHistoricalData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchRigData = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const blocksByHeight = state.networkData.blocksByHeight
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0 || !latestBlockHeight) {
      setTimeout(fetchRigData, 20000)
      return
    }
    const previousData = state.minerData.rigGpsData || []
    const previousRigShareData = state.minerData.rigShareData || {}
    const previousRigWorkers = state.minerData.rigWorkers || []
    let previousMaxBlockHeight = latestBlockHeight - BLOCK_RANGE
    for (const block in previousData) {
      if (block.height > previousMaxBlockHeight) previousMaxBlockHeight = block.height
    }
    const basicAuthString = basicAuth(state.auth.account.token)
    const url = `${API_URL_V2}worker/rigs/${id}/${latestBlockHeight},${BLOCK_RANGE}`
    const newRigDataResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuthString
      }
    })
    if (!newRigDataResponse.ok) return
    // console.log('newRigDataResponse is: ', newRigDataResponse)
    const newRigData = await newRigDataResponse.json()
    const formattedNewRigGpsData = {
      c29: [],
      c31: []
    }
    const previousRigWorkersWithoutTotal = previousRigWorkers.filter(item => item !== 'Total')
    const rigWorkers = [ 'Total', ...previousRigWorkersWithoutTotal ]
    let previousBlockData = { c29: {}, c31: {} }
    for (const blockHeight in newRigData) { // for each block
      const blockShareData = { height: parseInt(blockHeight), 'Total': { c29ValidShares: 0, c31ValidShares: 0 } }
      if (!blocksByHeight[blockHeight - 5]) continue
      const previousPeriodTimestamp = blocksByHeight[blockHeight - 5].timestamp
      const periodDuration = blocksByHeight[blockHeight].timestamp - previousPeriodTimestamp
      const blockTemplate = {
        height: parseInt(blockHeight),
        timestamp: blocksByHeight[blockHeight].timestamp,
        difficulty: blocksByHeight[blockHeight].difficulty,
        secondary_scaling: blocksByHeight[blockHeight].secondary_scaling
      }
      const block = {
        c29: { ...blockTemplate, Total: 0 },
        c31: { ...blockTemplate, Total: 0 }
      }
      for (const rig in newRigData[blockHeight]) {
        for (const worker in newRigData[blockHeight][rig]) {
          const rigWorkerKey = `${rig}-${worker}`
          blockShareData[`${rig}-${worker}`] = { c29ValidShares: 0, c31ValidShares: 0 }
          if (!rigWorkers.includes(rigWorkerKey)) rigWorkers.push(rigWorkerKey)
          for (const algo in newRigData[blockHeight][rig][worker]) {
            const numberShares = newRigData[blockHeight][rig][worker][algo].accepted
            blockShareData[`${rig}-${worker}`][`c${algo}ValidShares`] = numberShares
            blockShareData['Total'][`c${algo}ValidShares`] += numberShares
            const previousBlockGps = previousBlockData[`c${algo}`][rigWorkerKey]
            let currentPeriodGps
            if (algo === '29') {
              currentPeriodGps = numberShares * 21 / periodDuration
            } else {
              currentPeriodGps = numberShares * 42 / periodDuration
            }
            if (!previousBlockGps) {
              block[`c${algo}`][rigWorkerKey] = currentPeriodGps
              block[`c${algo}`]['Total'] += currentPeriodGps
            } else {
              // average gps with the last block to smoothe things out (10-minute average)
              block[`c${algo}`][rigWorkerKey] = (currentPeriodGps + previousBlockGps) / 2
              block[`c${algo}`]['Total'] += (currentPeriodGps + previousBlockGps) / 2
            }
          }
        }
      }
      formattedNewRigGpsData.c29.push(block.c29)
      formattedNewRigGpsData.c31.push(block.c31)
      previousBlockData = {
        c29: block.c29,
        c31: block.c31
      }
      previousRigShareData[`block_${blockHeight}`] = blockShareData
    }

    /*
    * minerShareData
    * { block_123123: { height: 123123, c29ValidShares: 52, c31ValidShares: 85 }}
    */

    console.log('formattedNewRigData is: ', formattedNewRigGpsData)
    dispatch({ type: 'RIG_DATA', data: { rigGpsData: formattedNewRigGpsData, rigShareData: previousRigShareData, rigWorkers } })
  } catch (e) {

  }
}

export const fetchMinerShareData = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const previousData = state.minerData.minerShareData
    let previousMaxBlockHeight = latestBlockHeight - BLOCK_RANGE
    const previousDataKeys = Object.keys(previousData)
    previousDataKeys.forEach(key => {
      const blockHeight = parseInt(key.replace('block_', ''))
      if (blockHeight > previousMaxBlockHeight) previousMaxBlockHeight = blockHeight
    })
    const blockDifference = latestBlockHeight - previousMaxBlockHeight
    const url = `${API_URL_V2}worker/shares/${id}/${latestBlockHeight},${blockDifference}`
    const minerSharesResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    if (!minerSharesResponse.ok) return
    const minerSharesData = await minerSharesResponse.json()
    const formattedMinerSharesData = { ...previousData }
    minerSharesData.forEach((shareData) => {
      if (formattedMinerSharesData[`block_${shareData.height}`]) {
        formattedMinerSharesData[`block_${shareData.height}`][`c${shareData.edge_bits}ValidShares`] = shareData.valid
      } else {
        formattedMinerSharesData[`block_${shareData.height}`] = {
          height: shareData.height,
          [`c${shareData.edge_bits}ValidShares`]: shareData.valid
        }
      }
    })
    dispatch({ type: 'MINER_SHARE_DATA', data: { minerShareData: formattedMinerSharesData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

// complete
export const fetchMinerTotalValidShares = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL_V2}worker/stat/${id}/total_valid_shares`
    const minerTotalValidSharesResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    if (!minerTotalValidSharesResponse.ok) return
    const minerShares = await minerTotalValidSharesResponse.json()
    dispatch({ type: 'MINER_TOTAL_VALID_SHARES', data: { totalSharesSubmitted: minerShares.total_valid_shares } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

// complete
export const fetchMinerPaymentData = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/utxo/${id}`
    console.log('url is: ', url)
    const minerPaymentResponse = await fetch(url, {
      headers: {
        authorization: basicAuthLegacy(state.auth.account.legacyToken)
      }
    })
    if (!minerPaymentResponse.ok) return
    const minerPaymentData = await minerPaymentResponse.json()
    if (minerPaymentData) {
      dispatch({ type: 'MINER_PAYMENT_DATA', data: minerPaymentData })
    }
  } catch (e) {
    console.log('Error: ', e)
  }
}

// complete: get latest miner payment (singular)
export const getLatestMinerPayments = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL_V2}worker/payment/${id}`
    const latestMinerPaymentResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    if (!latestMinerPaymentResponse.ok) return
    const latestMinerPaymentData = await latestMinerPaymentResponse.json()
    console.log('latestMinerPaymentData: ', latestMinerPaymentData)
  } catch (e) {
    console.log('Error: ', e)
  }
}

// complete
export const getLatestMinerPaymentRange = (range?: number = 200) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL_V2}worker/payments/${id}/${range}`
    const latestMinerPaymentResponse = await fetch(url, {
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    if (!latestMinerPaymentResponse.ok) return
    const latestMinerPaymentData = await latestMinerPaymentResponse.json()
    let totalPayoutsAmount = 0
    latestMinerPaymentData.forEach(payment => {
      if (payment.state === 'confirmed') {
        totalPayoutsAmount = totalPayoutsAmount + payment.amount
      }
    })
    console.log('latestMinerPaymentData: ', latestMinerPaymentData)
    dispatch({
      type: 'LATEST_MINER_PAYMENTS',
      data: {
        latestMinerPayments: latestMinerPaymentData,
        totalPayoutsAmount
      }
    })
  } catch (e) {
    console.log('Error: ', e)
  }
}

// NOT completed!
export const fetchMinerPaymentTxSlate = () => async (dispatch: Dispatch, getState: GetState) => {
  dispatch({
    type: 'IS_TX_SLATE_LOADING',
    data: true
  })
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL_V2}pool/payment/get_tx_slate/${id}`
    const minerPaymentTxSlateResponse = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': basicAuth(state.auth.account.token)
      }
    })
    if (!minerPaymentTxSlateResponse.ok) return
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

// NOT complete!
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
        authorization: basicAuthLegacy(state.auth.account.legacyToken)
      }
    }
    // need to discern between automated payments and manual
    if (formState.paymentType === 'manual') {
      const method = formState.paymentMethod
      const cleanedRecipient = formState.recipient
      const url = `${API_URL}pool/payment/${method}/${id}/${cleanedRecipient}`
      const requestPaymentResponse = await fetch(url, authorizedPost)
      const requestPaymentData = await requestPaymentResponse.json()
      if (!requestPaymentResponse.ok) {
        dispatch({
          type: 'MANUAL_PAYMENT_FAILURE',
          data: requestPaymentData
        })
      } else {
        const isSuccessful = requestPaymentData === 'ok'
        dispatch({
          type: 'MANUAL_PAYMENT_SUBMISSION',
          data: isSuccessful
        })
      }
    } else { // if they are saving a setting
      const methodUrl = `${API_URL_V2}worker/utxo/${id}/method/${formState.paymentMethod}`
      const setPaymentMethodResponse = await fetch(methodUrl, authorizedPost)
      if (!setPaymentMethodResponse.ok) return
      const setPaymentMethodData = await setPaymentMethodResponse.json()
      if (setPaymentMethodData.method !== formState.paymentMethod) throw new Error('Settings save failed!')
      const addressUrl = `${API_URL_V2}worker/utxo/${id}/address/${formState.recipient}`
      const setPaymentSettingResponse = await fetch(addressUrl, authorizedPost)
      if (!setPaymentSettingResponse.ok) return
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

export const fetchMinerImmatureBalance = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/estimate/payment/${id}`
    const fetchMinerImmatureBalanceResponse = await fetch(url, {
      headers: {
        authorization: basicAuthLegacy(state.auth.account.legacyToken)
      }
    })
    if (!fetchMinerImmatureBalanceResponse.ok) return
    const fetchMinerImmatureBalanceData = await fetchMinerImmatureBalanceResponse.json()
    if (isNaN(fetchMinerImmatureBalanceData.immature)) return
    dispatch({
      type: 'MINER_IMMATURE_BALANCE',
      data: fetchMinerImmatureBalanceData.immature
    })
  } catch (e) {
    console.log('fetchMinerImmatureBalance error: ', e)
  }
}

export const fetchMinerBlockReward = (height: number) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/estimate/payment/${id}/${height}`
    const fetchMinerBlockRewardResponse = await fetch(url, {
      headers: {
        authorization: basicAuthLegacy(state.auth.account.legacyToken)
      }
    })
    if (!fetchMinerBlockRewardResponse.ok) return
    const fetchMinerBlockRewardData = await fetchMinerBlockRewardResponse.json()
    if (isNaN(fetchMinerBlockRewardData[height])) return
    dispatch({
      type: 'MINER_BLOCK_REWARDS',
      data: fetchMinerBlockRewardData[height]
    })
  } catch (e) {
    console.log('fetchMinerBlockRewards error: ', e)
  }
}

export const fetchMinerLatestBlockReward = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const recentPoolBlocks = state.grinPoolData.recentBlocks.map(block => block.height)
    const latestPoolBlock = Math.max(...recentPoolBlocks)
    const url = `${API_URL}worker/estimate/payment/${id}/${latestPoolBlock}`
    const fetchMinerLatestBlockRewardResponse = await fetch(url, {
      headers: {
        authorization: basicAuthLegacy(state.auth.account.legacyToken)
      }
    })
    if (!fetchMinerLatestBlockRewardResponse.ok) return
    const fetchMinerLatestBlockRewardData = await fetchMinerLatestBlockRewardResponse.json()
    if (isNaN(fetchMinerLatestBlockRewardData[latestPoolBlock])) return
    dispatch({
      type: 'MINER_LATEST_BLOCK_GRIN_EARNED',
      data: fetchMinerLatestBlockRewardData[latestPoolBlock]
    })
  } catch (e) {
    console.log('fetchMinerBlockRewards error: ', e)
  }
}

export const fetchMinerNextBlockReward = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const id = state.auth.account.id
    const url = `${API_URL}worker/estimate/payment/${id}/next`
    const fetchMinerNextBlockRewardResponse = await fetch(url, {
      headers: {
        authorization: basicAuthLegacy(state.auth.account.legacyToken)
      }
    })
    if (!fetchMinerNextBlockRewardResponse.ok) return
    const fetchMinerNextBlockRewardData = await fetchMinerNextBlockRewardResponse.json()
    if (isNaN(fetchMinerNextBlockRewardData.next)) return
    dispatch({
      type: 'MINER_NEXT_BLOCK_GRIN_EARNED',
      data: fetchMinerNextBlockRewardData.next
    })
  } catch (e) {
    console.log('fetchMinerBlockRewards error: ', e)
  }
}
