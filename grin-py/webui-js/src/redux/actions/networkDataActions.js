import { API_URL } from '../../config.js'

const BLOCK_RANGE = 180

export const fetchNetworkData = (start: number = 0) => async (dispatch) => {
  try {
    const latestBlock = await getLatestBlock()
    const url = `${API_URL}stats/${latestBlock},${BLOCK_RANGE}/gps,height,difficulty`
    const networkDataResponse = await fetch(url)
    const networkData = await networkDataResponse.json()
    dispatch({ type: 'NETWORK_DATA', data: networkData })
  } catch (e) {
    console.log('Error: ', e)
  }
}

export const getLatestBlock = async () => {
  try {
    const latestBlockUrl = `${API_URL}block`
    const latestBlockResponse = await fetch(latestBlockUrl)
    const latestBlockData = await latestBlockResponse.json()
    // action('LATEST_BLOCK_DATA', { latestBlockData })
    return latestBlockData.height
  } catch (e) {
    console.log('error: ', e)
  }
}
