// @flow
import { API_URL } from '../../config.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'

export const fetchGrinPoolData = (start: number = 0) => async (dispatch, getState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}pool/stats/${latestBlockHeight},${BLOCK_RANGE}/gps,height,total_blocks_found`
    const grinPoolDataResponse = await fetch(url)
    const grinPoolData = await grinPoolDataResponse.json()
    dispatch({ type: 'GRIN_POOL_DATA', data: { historical: grinPoolData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolActiveMinerCount = (start: number = 0) => async (dispatch, getState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}worker/stats/${latestBlockHeight},1/worker`
    const activeWorkersDataResponse = await fetch(url)
    const activeWorkersData = await activeWorkersDataResponse.json()
    dispatch({ type: 'GRIN_POOL_ACTIVE_WORKERS', data: { activeWorkers: activeWorkersData.length } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolLastBlock = (start: number = 0) => async (dispatch) => {
  try {
    const url = `${API_URL}pool/block`
    const grinPoolLastBlockDataResponse = await fetch(url)
    const grinPoolLastBlockData = await grinPoolLastBlockDataResponse.json()
    dispatch({ type: 'GRIN_POOL_LAST_BLOCK_MINED', data: { lastBlockMined: grinPoolLastBlockData.timestamp } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolSharesSubmitted = (start: number = 0) => async (dispatch, getState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}pool/stats/${latestBlockHeight},${BLOCK_RANGE}/shares_processed,total_shares_processed,height`
    const sharesSubmittedDataResponse = await fetch(url)
    const sharesSubmittedData = await sharesSubmittedDataResponse.json()
    dispatch({ type: 'GRIN_POOL_SHARES_SUBMITTED', data: { sharesSubmittedData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}
