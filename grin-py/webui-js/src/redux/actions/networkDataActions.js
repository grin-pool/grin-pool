// @flow
import { API_URL } from '../../config.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import { type Dispatch, type GetState } from '../types.js'
import { fetchGrinPoolBlocksMined } from './grinPoolDataActions.js'

export const fetchNetworkData = (start: number = 0) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const latestBlockHeight = state.networkData.latestBlock.height || 0
    const url = `${API_URL}grin/stats/${latestBlockHeight},${BLOCK_RANGE}/gps,height,difficulty,timestamp`
    const networkDataResponse = await fetch(url)
    const networkData = await networkDataResponse.json()
    dispatch({ type: 'NETWORK_DATA', data: { historical: networkData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const getLatestBlock = () => async (dispatch: Dispatch) => {
  try {
    const latestBlockUrl = `${API_URL}grin/block`
    const latestBlockResponse = await fetch(latestBlockUrl)
    const latestBlockData = await latestBlockResponse.json()
    // for null response
    // const latestBlockData = {
    //  'height': 0
    // }
    dispatch({ type: 'LATEST_BLOCK', data: { latestBlock: latestBlockData } })
  } catch (e) {
    console.log('error: ', e)
  }
}

export const fetchNetworkRecentBlocks = (endBlock: number | null = null, range: number = 20) => async (dispatch: Dispatch, getState: GetState) => {
  try {
    const state = getState()
    const blockHeight = endBlock || state.networkData.latestBlock.height || 0
    const url = `${API_URL}grin/blocks/${blockHeight},${range}`
    const networkRecentBlocksResponse = await fetch(url)
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
    const increasedBlockRange = 4 * BLOCK_RANGE
    const minedBlockAlgosUrl = `${API_URL}grin/blocks/${latestBlockHeight},${increasedBlockRange}/height,edge_bits`
    const minedBlockAlgosResponse = await fetch(minedBlockAlgosUrl)
    const minedBlockAlgosData = await minedBlockAlgosResponse.json()
    const algos = {
      c29: [],
      c31: []
    }
    minedBlockAlgosData.forEach(block => {
      if (block.edge_bits === 29) {
        algos.c29.push(block.height)
      }
      if (block.edge_bits === 31) {
        algos.c31.push(block.height)
      }
    })
    dispatch({ type: 'MINED_BLOCKS_ALGOS', data: algos })
    dispatch(fetchGrinPoolBlocksMined())
  } catch (e) {
    console.log('error: ', e)
  }
}
