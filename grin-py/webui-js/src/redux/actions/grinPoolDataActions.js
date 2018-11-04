// @flow
import { API_URL } from '../../config.js'
import { getLatestBlock } from './networkDataActions.js'

const BLOCK_RANGE = 120

export const fetchGrinPoolData = (start: number = 0) => async (dispatch) => {
  try {
    const latestBlockData = await getLatestBlock()
    const latestBlockHeight = latestBlockData.height
    const url = `${API_URL}pool/stats/${latestBlockHeight},${BLOCK_RANGE}/gps,height`
    console.log('url is: ', url)
    const grinPoolDataResponse = await fetch(url)
    const grinPoolData = await grinPoolDataResponse.json()
    dispatch({ type: 'GRIN_POOL_DATA', data: { historical: grinPoolData } })
  } catch (e) {
    console.log('Error: ', e)
  }
}
