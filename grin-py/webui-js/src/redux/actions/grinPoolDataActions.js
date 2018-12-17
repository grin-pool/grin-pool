// @flow
import { API_URL } from '../../config.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import { type Dispatch, type GetState } from '../types.js'

export const fetchGrinPoolData = (start: number = 0) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}pool/stats/${latestBlockHeight},${BLOCK_RANGE}/gps,height,total_blocks_found,active_miners,timestamp`
    const grinPoolDataResponse = await fetch(url)
    const grinPoolData = await grinPoolDataResponse.json()
    dispatch({ type: 'GRIN_POOL_DATA', data: { historical: grinPoolData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolLastBlock = (start: number = 0) => async (dispatch: Dispatch) => {
  try {
    const url = `${API_URL}pool/block`
    const grinPoolLastBlockDataResponse = await fetch(url)
    const grinPoolLastBlockData = await grinPoolLastBlockDataResponse.json()
    dispatch({ type: 'GRIN_POOL_LAST_BLOCK_MINED', data: { lastBlockMined: grinPoolLastBlockData.timestamp } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolRecentBlocks = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}pool/blocks/${latestBlockHeight},86400`
    const grinPoolRecentBlocksResponse = await fetch(url)
    const grinPoolRecentBlocksData = await grinPoolRecentBlocksResponse.json()
    dispatch({
      type: 'GRIN_POOL_RECENT_BLOCKS',
      data: grinPoolRecentBlocksData
    })
  } catch (e) {

  }
}

export const fetchGrinPoolSharesSubmitted = (start: number = 0) => async (dispatch: Dispatch, getState: GetState) => {
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

export const fetchGrinPoolBlocksMined = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}pool/blocks/${latestBlockHeight},${BLOCK_RANGE}`
    const grinPoolBlocksMinedResponse = await fetch(url)
    const grinPoolBlocksMinedData = await grinPoolBlocksMinedResponse.json()
    // turn them into a basic array
    const blocksFound = grinPoolBlocksMinedData.map((block) => {
      return block.height
    })
    dispatch({
      type: 'POOL_BLOCKS_MINED',
      data: blocksFound
    })
  } catch (e) {

  }
}
