
import { connect } from 'react-redux'
import { BlockRange } from '../../containers/BlockRange/BlockRange.js'
import { fetchNetworkRecentBlocks } from '../actions/networkDataActions.js'

const mapStateToProps = (state) => {
  return {
    latestBlockHeight: state.networkData.latestBlock.height,
    recentBlocks: state.networkData.recentBlocks || [],
    graphTitle: 'Network Block Info'
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchBlockRange: (endBlockHeight?: null | number, rangeSize?: number) => dispatch(fetchNetworkRecentBlocks(endBlockHeight, rangeSize))
  }
}

export const NetworkRecentBlocksConnector = connect(mapStateToProps, mapDispatchToProps)(BlockRange)
