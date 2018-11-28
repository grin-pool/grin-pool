
import { connect } from 'react-redux'
import { MinerPaymentDataComponent } from '../../containers/MinerPayment/MinerPaymentData.js'
import { fetchMinerPaymentData } from '../actions/minerDataActions.js'

const mapStateToProps = (state) => {
  const paymentData = state.minerData.paymentData
  return {
    amount: paymentData.amount,
    address: paymentData.address,
    lastSuccess: paymentData.last_success,
    failureCount: paymentData.failure_count,
    lastTry: paymentData.last_try,
    currentTimestamp: Date.now() / 1000
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchMinerPaymentData: () => dispatch(fetchMinerPaymentData())
  }
}

export const MinerPaymentDataConnector = connect(mapStateToProps, mapDispatchToProps)(MinerPaymentDataComponent)
