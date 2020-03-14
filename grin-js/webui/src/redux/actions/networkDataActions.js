// @flow
import { API_URL_V2 } from '../../config.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import { logout } from './authActions.js'
import { type Dispatch, type GetState } from '../../types.js'
import { fetchGrinPoolBlocksMined } from './grinPoolDataActions.js'

export const fetchNetworkData = (start: number = 0) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const previousData = state.networkData.historical
    const previousBlocksByHeight = state.networkData.blocksByHeight
    let previousMaxBlockHeight: number = latestBlockHeight - BLOCK_RANGE
    previousData.forEach(block => {
      if (block.height > previousMaxBlockHeight) previousMaxBlockHeight = block.height
    })
    const blockDifference = latestBlockHeight - previousMaxBlockHeight
    const url = `${API_URL_V2}grin/stats/${latestBlockHeight},${blockDifference}/gps,height,difficulty,timestamp,secondary_scaling`
    const newNetworkDataResponse = await fetch(url)
    if (!newNetworkDataResponse.ok) return
    const newNetworkData = await newNetworkDataResponse.json()
    for (const block in previousBlocksByHeight) {
      if (block.height < latestBlockHeight - 1440 - 240) delete previousBlocksByHeight[block.height]
    }
    newNetworkData.forEach((block) => {
      previousBlocksByHeight[block.height] = {
        timestamp: block.timestamp,
        difficulty: block.difficulty,
        secondary_scaling: block.secondary_scaling
      }
    })
    const concatenatedNetworkData = [...previousData, ...newNetworkData]
    const numberToRemove = concatenatedNetworkData.length > BLOCK_RANGE ? concatenatedNetworkData.length - BLOCK_RANGE : 0
    const newHistoricalData = concatenatedNetworkData.slice(numberToRemove)

    dispatch({ type: 'NETWORK_DATA', data: { historical: newHistoricalData, blocksByHeight: previousBlocksByHeight } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const getLatestBlock = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    if (state.auth.account) {
      const expirationTimestamp = parseInt(state.auth.account.expirationTimestamp)
      const currentTimestamp = new Date().getTime() / 1000
      if (expirationTimestamp < currentTimestamp) dispatch(logout())
    }
    const latestBlockUrl = `${API_URL_V2}grin/block`
    const latestBlockResponse = await fetch(latestBlockUrl)
    if (!latestBlockResponse.ok) return
    let latestBlockData = await latestBlockResponse.json()
    // for null response
    if (latestBlockData === null) {
      latestBlockData = {
        'height': 0
      }
    }
    dispatch({ type: 'LATEST_BLOCK', data: { latestBlock: latestBlockData } })
  } catch (e) {
    console.log('error: ', e)
  }
}

export const fetchNetworkRecentBlocks = (endBlock: number | null = null, range: number = 20) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = endBlock || state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const url = `${API_URL_V2}grin/blocks/${latestBlockHeight},${range}`
    const networkRecentBlocksResponse = await fetch(url)
    if (!networkRecentBlocksResponse.ok) return
    const networkRecentBlocksData = await networkRecentBlocksResponse.json()
    // const blocksOrphaned = grinPoolRecentBlocksData.filter((block) => block.state === 'orphan')
    // console.log('fetchGrinPoolRecentBlocks blocksOrphaned: ', blocksOrphaned)
    dispatch({
      type: 'NETWORK_RECENT_BLOCKS',
      data: networkRecentBlocksData
    })
  } catch (e) {

  }
}

export const getMinedBlocksAlgos = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const previousData = state.networkData.minedBlockAlgos
    let previousMaxBlockHeight = latestBlockHeight - BLOCK_RANGE
    const combinedMax = Math.max(Math.max(...previousData.c29), Math.max(...previousData.c31))
    if (combinedMax > previousMaxBlockHeight) previousMaxBlockHeight = combinedMax
    const blockDifference = latestBlockHeight - previousMaxBlockHeight
    const minedBlockAlgosUrl = `${API_URL_V2}grin/blocks/${latestBlockHeight},${blockDifference}/height,edge_bits`
    const minedBlockAlgosResponse = await fetch(minedBlockAlgosUrl)
    if (!minedBlockAlgosResponse.ok) return
    const minedBlockAlgosData = await minedBlockAlgosResponse.json()
    const newBlockAlgos = {
      c29: [],
      c31: []
    }
    minedBlockAlgosData.forEach(block => {
      if (block.edge_bits === 29) {
        newBlockAlgos.c29.push(block.height)
      }
      if (block.edge_bits === 31) {
        newBlockAlgos.c31.push(block.height)
      }
    })
    const updatedBlockAlgos = {
      c29: [...previousData.c29, ...newBlockAlgos.c29],
      c31: [...previousData.c31, ...newBlockAlgos.c31]
    }
    updatedBlockAlgos.c29.filter(height => (height > latestBlockHeight - BLOCK_RANGE))
    updatedBlockAlgos.c31.filter(height => (height > latestBlockHeight - BLOCK_RANGE))
    dispatch({ type: 'MINED_BLOCKS_ALGOS', data: updatedBlockAlgos })
    dispatch(fetchGrinPoolBlocksMined())
  } catch (e) {
    console.log('error: ', e)
  }
}
