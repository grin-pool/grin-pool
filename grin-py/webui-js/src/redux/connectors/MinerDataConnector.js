
import { connect } from 'react-redux'
import { MinerDataComponent } from '../../containers/MinerData/MinerData.js'
import { fetchMinerData } from '../actions/minerDataActions.js'

const mapStateToProps = (state) => ({
  minerData: state.minerData.historical || [],
  latestBlockHeight: state.networkData.latestBlock.height || 0,
  poolBlocksMined: state.grinPoolData.poolBlocksMined || [],
  estimatedHourlyReturn: state.minerData.minerImmatureBalance.est_hour_return || 0,
  latestBlock: state.networkData.latestBlock || 0

})

const mapDispatchToProps = (dispatch) => {
  return {
    fetchMinerData: () => dispatch(fetchMinerData())
  }
}

export const MinerDataConnector = connect(mapStateToProps, mapDispatchToProps)(MinerDataComponent)
