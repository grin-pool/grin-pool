
import { connect } from 'react-redux'
import { BlockRange } from '../../containers/BlockRange/BlockRange.js'
import { fetchGrinPoolRecentBlocks } from '../actions/grinPoolDataActions.js'

const mapStateToProps = (state) => {
  return {
    latestBlockHeight: state.networkData.latestBlock.height,
    recentBlocks: state.grinPoolData.recentBlocks || [],
    graphTitle: 'Blocks Found by Pool'
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchBlockRange: () => dispatch(fetchGrinPoolRecentBlocks())
  }
}

export const GrinPoolRecentBlocksConnector = connect(mapStateToProps, mapDispatchToProps)(BlockRange)
