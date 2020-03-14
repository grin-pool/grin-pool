
import { connect } from 'react-redux'
import { MinerDetailsComponent } from '../../containers/MinerDetails/MinerDetails.js'

const mapStateToProps = (state) => {
  return {
    // username: state.auth.account.username
  }
}

const mapDispatchToProps = (dispatch) => {
  return {

  }
}

export const MinerDetailsConnector = connect(mapStateToProps, mapDispatchToProps)(MinerDetailsComponent)
