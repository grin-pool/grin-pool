
import { connect } from 'react-redux'
import { MinerPaymentDataComponent } from '../../containers/MinerPayment/MinerPaymentData.js'
import { fetchMinerPaymentData, fetchMinerImmatureBalance } from '../actions/minerDataActions.js'

const mapStateToProps = (state) => {
  const paymentData = state.minerData.paymentData
  return {
    amount: paymentData.amount || 0,
    address: paymentData.address,
    lastSuccess: paymentData.last_success,
    failureCount: paymentData.failure_count,
    lastTry: paymentData.last_try,
    currentTimestamp: Date.now() / 1000,
    lastestBlockHeight: state.networkData.latestBlock.height,
    minerImmatureBalance: state.minerData.minerImmatureBalance || 0,
    totalPayoutsAmount: state.minerData.totalPayoutsAmount
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchMinerPaymentData: () => dispatch(fetchMinerPaymentData()),
    fetchMinerImmatureBalance: () => dispatch(fetchMinerImmatureBalance())
  }
}

export const MinerPaymentDataConnector = connect(mapStateToProps, mapDispatchToProps)(MinerPaymentDataComponent)
