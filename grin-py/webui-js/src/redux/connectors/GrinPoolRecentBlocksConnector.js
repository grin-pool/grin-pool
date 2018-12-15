
import { connect } from 'react-redux'
import { GrinPoolRecentBlocks } from '../../containers/GrinPoolData/GrinPoolRecentBlocks.js'
import { fetchGrinPoolRecentBlocks } from '../actions/grinPoolDataActions.js'

const mapStateToProps = (state) => {
  return {
    recentBlocks: state.grinPoolData.recentBlocks || []
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchGrinPoolRecentBlocks: () => dispatch(fetchGrinPoolRecentBlocks())
  }
}

export const GrinPoolRecentBlocksConnector = connect(mapStateToProps, mapDispatchToProps)(GrinPoolRecentBlocks)
