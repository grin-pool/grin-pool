
import { connect } from 'react-redux'
import { MiningGraphComponent } from '../../containers/MiningGraph/MiningGraph.js'
import { getMinedBlocksAlgos } from '../actions/networkDataActions'

const mapStateToProps = (state) => ({
  minedBlockAlgos: state.networkData.minedBlockAlgos,
  poolBlocksMined: state.grinPoolData.poolBlocksMined,
  latestBlockHeight: state.networkData.latestBlock.height || 0
})

const mapDispatchToProps = (dispatch) => {
  return {
    getMinedBlocksAlgos: () => dispatch(getMinedBlocksAlgos())
  }
}

export const MiningGraphConnector = connect(mapStateToProps, mapDispatchToProps)(MiningGraphComponent)
