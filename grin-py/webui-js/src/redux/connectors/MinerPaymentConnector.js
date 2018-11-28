
import { connect } from 'react-redux'
import { MinerPaymentComponent } from '../../containers/MinerPayment/MinerPayment.js'

const mapStateToProps = (state) => ({
  // username: state.auth.account.username
})

const mapDispatchToProps = (dispatch) => {
  return {

  }
}

export const MinerPaymentConnector = connect(mapStateToProps, mapDispatchToProps)(MinerPaymentComponent)
