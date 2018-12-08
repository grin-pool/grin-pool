
import { connect } from 'react-redux'
import { GrinPoolDataComponent } from '../../containers/GrinPoolData/GrinPoolData.js'
import {
  fetchGrinPoolData,
  fetchGrinPoolLastBlock
} from '../actions/grinPoolDataActions.js'

const mapStateToProps = (state) => {
  const grinPoolHistoricalData = state.grinPoolData.historical
  const grinPoolHistoricalDataLength = grinPoolHistoricalData.length
  const poolBlocksMined = state.grinPoolData.poolBlocksMined
  const latestBlockHeight = state.networkData.latestBlock.height
  let activeWorkers = 0
  if (grinPoolHistoricalDataLength > 0) {
    activeWorkers = grinPoolHistoricalData[grinPoolHistoricalDataLength - 1].active_miners
  }
  return {
    networkData: state.grinPoolData.historical || [],
    activeWorkers,
    lastBlockMined: state.grinPoolData.lastBlockMined,
    poolBlocksMined,
    latestBlockHeight
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchGrinPoolData: () => dispatch(fetchGrinPoolData()),
    fetchGrinPoolLastBlock: () => dispatch(fetchGrinPoolLastBlock())
  }
}

export const GrinPoolDataConnector = connect(mapStateToProps, mapDispatchToProps)(GrinPoolDataComponent)
