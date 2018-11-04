
import { connect } from 'react-redux'
import { NetworkDataComponent } from '../../containers/NetworkData/NetworkData.js'
import { fetchGrinPoolData } from '../actions/grinPoolDataActions.js'

const mapStateToProps = (state) => {
  return {
    networkData: state.grinPoolData.historical || [],
    latestBlock: state.networkData.latestBlock || 0
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchNetworkData: () => dispatch(fetchGrinPoolData())
  }
}

export const GrinPoolDataConnector = connect(mapStateToProps, mapDispatchToProps)(NetworkDataComponent)
