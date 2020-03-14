
import { connect } from 'react-redux'
import { RigDetailsComponent } from '../../containers/RigDetails/RigDetails.js'

const mapStateToProps = (state) => {
  return {
    // username: state.auth.account.username
  }
}

const mapDispatchToProps = (dispatch) => {
  return {

  }
}

export const RigDetailsConnector = connect(mapStateToProps, mapDispatchToProps)(RigDetailsComponent)
