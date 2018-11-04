
import { connect } from 'react-redux'
import { GrinPoolDataComponent } from '../../containers/GrinPoolData/GrinPoolData.js'
import {
  fetchGrinPoolData,
  fetchGrinPoolActiveMinerCount,
  fetchGrinPoolLastBlock
} from '../actions/grinPoolDataActions.js'

const mapStateToProps = (state) => {
  return {
    networkData: state.grinPoolData.historical || [],
    activeWorkers: state.grinPoolData.activeWorkers,
    lastBlockMined: state.grinPoolData.lastBlockMined
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchNetworkData: () => dispatch(fetchGrinPoolData()),
    fetchGrinPoolActiveMinerCount: () => dispatch(fetchGrinPoolActiveMinerCount()),
    fetchGrinPoolLastBlock: () => dispatch(fetchGrinPoolLastBlock())
  }
}

export const GrinPoolDataConnector = connect(mapStateToProps, mapDispatchToProps)(GrinPoolDataComponent)
