
import { connect } from 'react-redux'
import { NetworkDataComponent } from '../../containers/NetworkData/NetworkData.js'
import { fetchNetworkData } from '../actions/networkDataActions.js'

const mapStateToProps = (state) => {
  const networkData = state.networkData.historical || []
  const latestBlock = state.networkData.latestBlock || 0
  return {
    networkData,
    latestBlock
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchNetworkData: () => dispatch(fetchNetworkData())
  }
}

export const NetworkDataConnector = connect(mapStateToProps, mapDispatchToProps)(NetworkDataComponent)
