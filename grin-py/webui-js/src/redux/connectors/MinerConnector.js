
import { connect } from 'react-redux'
import { MinerComponent } from '../../containers/Miner/Miner.js'

const mapStateToProps = (state) => ({
  username: state.auth.account.username
})

const mapDispatchToProps = (dispatch) => {
  return {

  }
}

export const MinerConnector = connect(mapStateToProps, mapDispatchToProps)(MinerComponent)
