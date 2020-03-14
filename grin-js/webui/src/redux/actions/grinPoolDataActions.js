// @flow
import { API_URL_V2 } from '../../config.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import { type Dispatch, type GetState } from '../../types.js'

export const fetchGrinPoolData = (start: number = 0) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const previousData = state.grinPoolData.historical
    let previousMaxBlockHeight = latestBlockHeight - BLOCK_RANGE
    previousData.forEach(block => {
      if (block.height > previousMaxBlockHeight) previousMaxBlockHeight = block.height
    })
    const blockDifference = latestBlockHeight - previousMaxBlockHeight
    const url = `${API_URL_V2}pool/stats/${latestBlockHeight},${blockDifference}/gps,height,total_blocks_found,active_miners,timestamp,edge_bits`
    const newGrinPoolDataResponse = await fetch(url)
    if (!newGrinPoolDataResponse.ok) return
    const newGrinPoolData = await newGrinPoolDataResponse.json()
    const newFormattedGrinPoolData = newGrinPoolData.map((block) => {
      return {
        ...block,
        share_counts: JSON.parse(block.share_counts)
      }
    })
    const concatenatedGrinPoolData = [...previousData, ...newFormattedGrinPoolData]
    const numberToRemove = concatenatedGrinPoolData.length > BLOCK_RANGE ? concatenatedGrinPoolData.length - BLOCK_RANGE : 0
    const newHistoricalData = concatenatedGrinPoolData.slice(numberToRemove)
    dispatch({ type: 'GRIN_POOL_DATA', data: { historical: newHistoricalData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolLastBlock = (start: number = 0) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const url = `${API_URL_V2}pool/block`
    const grinPoolLastBlockDataResponse = await fetch(url)
    if (!grinPoolLastBlockDataResponse.ok) return
    const grinPoolLastBlockData = await grinPoolLastBlockDataResponse.json()
    dispatch({ type: 'GRIN_POOL_LAST_BLOCK_MINED', data: { lastBlockMined: grinPoolLastBlockData.timestamp } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolRecentBlocks = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const minedBlockAlgos = state.networkData.minedBlockAlgos
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const url = `${API_URL_V2}pool/blocks/${latestBlockHeight},20`
    const grinPoolRecentBlocksResponse = await fetch(url)
    if (!grinPoolRecentBlocksResponse.ok) return
    const grinPoolRecentBlocksData = await grinPoolRecentBlocksResponse.json()
    const grinPoolRecentBlockWithEdgeBits = grinPoolRecentBlocksData.map(block => {
      let edge_bits = 29
      if (minedBlockAlgos.c31.includes(block.height)) edge_bits = 31
      return {
        ...block,
        edge_bits
      }
    })
    dispatch({
      type: 'GRIN_POOL_RECENT_BLOCKS',
      data: grinPoolRecentBlockWithEdgeBits
    })
  } catch (e) {

  }
}

export const fetchGrinPoolSharesSubmitted = (start: number = 0) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    const previousData = state.grinPoolData.sharesSubmitted
    let previousMaxBlockHeight = latestBlockHeight - BLOCK_RANGE
    previousData.forEach(block => {
      if (block.height > previousMaxBlockHeight) previousMaxBlockHeight = block.height
    })
    const blockDifference = latestBlockHeight - previousMaxBlockHeight
    const url = `${API_URL_V2}pool/stats/${latestBlockHeight},${blockDifference}/shares_processed,total_shares_processed,active_miners,height`
    const newSharesSubmittedDataResponse = await fetch(url)
    if (!newSharesSubmittedDataResponse.ok) return
    const newSharesSubmittedData = await newSharesSubmittedDataResponse.json()
    const concatenatedGrinPoolShareData = [...previousData, ...newSharesSubmittedData]
    const numberToRemove = concatenatedGrinPoolShareData.length > BLOCK_RANGE ? concatenatedGrinPoolShareData.length - BLOCK_RANGE : 0
    const sharesSubmittedData = concatenatedGrinPoolShareData.slice(numberToRemove)
    dispatch({ type: 'GRIN_POOL_SHARES_SUBMITTED', data: { sharesSubmittedData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const fetchGrinPoolBlocksMined = () => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const minedBlockAlgos = state.networkData.minedBlockAlgos
    const previousData = {
      ...state.grinPoolData.poolBlocksMined,
      orphaned: state.grinPoolData.poolBlocksOrphaned
    }
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    if (latestBlockHeight === 0) return
    let combinedMaxBlockHeight = Math.max(Math.max(...previousData.c29), Math.max(...previousData.c31), Math.max(...previousData.orphaned))
    combinedMaxBlockHeight = isFinite(combinedMaxBlockHeight) ? combinedMaxBlockHeight : 0
    const blockDifference = combinedMaxBlockHeight ? (latestBlockHeight - combinedMaxBlockHeight) : BLOCK_RANGE
    const url = `${API_URL_V2}pool/blocks/${latestBlockHeight},${blockDifference}`
    const grinPoolBlocksMinedResponse = await fetch(url)
    if (!grinPoolBlocksMinedResponse.ok) return
    const grinPoolBlocksMinedData = await grinPoolBlocksMinedResponse.json()
    // turn them into a basic array
    const c29BlocksFound = []
    const c31BlocksFound = []
    const c29BlocksWithTimestamps = {}
    const c31BlocksWithTimestamps = {}
    const blocksOrphaned = []
    grinPoolBlocksMinedData.forEach((block) => {
      if (block.state === 'new') {
        if (minedBlockAlgos.c29.includes(block.height)) {
          c29BlocksFound.push(block.height)
          c29BlocksWithTimestamps[block.height] = { height: block.height, timestamp: block.timestamp }
        }
        if (minedBlockAlgos.c31.includes(block.height)) {
          c31BlocksFound.push(block.height)
          c31BlocksWithTimestamps[block.height] = { height: block.height, timestamp: block.timestamp }
        }
      } else if (block.state === 'orphan') {
        blocksOrphaned.push(block.height)
      }
    })
    const updatedPoolBlocksMined = {
      c29: [...previousData.c29, ...c29BlocksFound],
      c31: [...previousData.c31, ...c31BlocksFound],
      orphaned: [...previousData.orphaned, ...blocksOrphaned],
      c29WithTimestamps: { ...previousData.c29BlocksWithTimestamps, ...c29BlocksWithTimestamps },
      c31WithTimestamps: { ...previousData.c31BlocksWithTimestamps, ...c31BlocksWithTimestamps }
    }
    updatedPoolBlocksMined.c29.filter(height => (height > latestBlockHeight - BLOCK_RANGE))
    updatedPoolBlocksMined.c31.filter(height => (height > latestBlockHeight - BLOCK_RANGE))
    updatedPoolBlocksMined.orphaned.filter(height => (height > latestBlockHeight - BLOCK_RANGE))
    dispatch({
      type: 'POOL_BLOCKS_MINED',
      data: {
        c29BlocksFound: updatedPoolBlocksMined.c29,
        c31BlocksFound: updatedPoolBlocksMined.c31,
        blocksOrphaned: updatedPoolBlocksMined.orphaned,
        c29BlocksWithTimestamps: updatedPoolBlocksMined.c29WithTimestamps,
        c31BlocksWithTimestamps: updatedPoolBlocksMined.c31WithTimestamps
      }
    })
  } catch (e) {
    console.log('getchGrinPoolBlocksMined error: ', e)
  }
}
