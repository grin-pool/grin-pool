
import { connect } from 'react-redux'
import { MinerSharesComponent } from '../../containers/MinerData/MinerShares.js'
import { fetchMinerData, fetchMinerTotalValidShares } from '../actions/minerDataActions.js'

const mapStateToProps = (state) => ({
  minerData: state.minerData.historical || [],
  totalSharesSubmitted: state.minerData.totalSharesSubmitted,
  latestBlockHeight: state.networkData.latestBlock.height || 0
})

const mapDispatchToProps = (dispatch) => {
  return {
    fetchMinerData: () => dispatch(fetchMinerData()),
    fetchMinerTotalValidShares: () => dispatch(fetchMinerTotalValidShares())
  }
}

export const MinerSharesConnector = connect(mapStateToProps, mapDispatchToProps)(MinerSharesComponent)
