
import { connect } from 'react-redux'
import { LatestMinerPayments } from '../../containers/MinerPayment/LatestMinerPayments.js'
import {
  getLatestMinerPaymentRange
} from '../actions/minerDataActions.js'

const mapStateToProps = (state) => ({
  lastestBlockHeight: state.networkData.latestBlock.height,
  latestMinerPayments: state.minerData.latestMinerPayments
})

const mapDispatchToProps = (dispatch) => {
  return {
    getLatestMinerPaymentRange: () => dispatch(getLatestMinerPaymentRange())
  }
}

export const LatestMinerPaymentsConnector = connect(mapStateToProps, mapDispatchToProps)(LatestMinerPayments)
