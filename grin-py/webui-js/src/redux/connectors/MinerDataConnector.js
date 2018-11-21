
import { connect } from 'react-redux'
import { MinerDataComponent } from '../../containers/MinerData/MinerData.js'
import { fetchMinerData } from '../actions/minerDataActions.js'

const mapStateToProps = (state) => ({
  minerData: state.minerData.historical || []
})

const mapDispatchToProps = (dispatch) => {
  return {
    fetchMinerData: () => dispatch(fetchMinerData())
  }
}

export const MinerDataConnector = connect(mapStateToProps, mapDispatchToProps)(MinerDataComponent)
