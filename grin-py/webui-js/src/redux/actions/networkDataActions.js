import { API_URL } from '../../config.js'

const BLOCK_RANGE = 120

export const fetchNetworkData = (start: number = 0) => async (dispatch) => {
  try {
    const latestBlockData = await getLatestBlock()
    const latestBlockHeight = latestBlockData.height
    const url = `${API_URL}grin/stats/${latestBlockHeight},${BLOCK_RANGE}/gps,height,difficulty`
    const networkDataResponse = await fetch(url)
    const networkData = await networkDataResponse.json()
    dispatch({ type: 'NETWORK_DATA', data: { historical: networkData, latestBlock: latestBlockData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const getLatestBlock = async () => {
  try {
    const latestBlockUrl = `${API_URL}grin/block`
    const latestBlockResponse = await fetch(latestBlockUrl)
    const latestBlockData = await latestBlockResponse.json()
    return latestBlockData
  } catch (e) {
    console.log('error: ', e)
  }
}
