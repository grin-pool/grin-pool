
import { connect } from 'react-redux'
import { RigGraphComponent } from '../../containers/RigGraph/RigGraph.js'
import { getMinedBlocksAlgos } from '../actions/networkDataActions.js'
import { fetchRigData } from '../actions/minerDataActions.js'

const mapStateToProps = (state) => ({
  minedBlockAlgos: state.networkData.minedBlockAlgos,
  rigGpsData: state.minerData.rigGpsData,
  rigWorkers: state.minerData.rigWorkers,
  poolBlocksMined: state.grinPoolData.poolBlocksMined,
  poolBlocksOrphaned: state.grinPoolData.poolBlocksOrphaned,
  latestBlockHeight: state.networkData.latestBlock.height || 0
})

const mapDispatchToProps = (dispatch) => {
  return {
    getMinedBlocksAlgos: () => dispatch(getMinedBlocksAlgos()),
    fetchRigData: () => dispatch(fetchRigData())
  }
}

export const RigGraphConnector = connect(mapStateToProps, mapDispatchToProps)(RigGraphComponent)
