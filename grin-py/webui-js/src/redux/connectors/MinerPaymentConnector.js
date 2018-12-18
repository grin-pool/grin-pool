
import { connect } from 'react-redux'
import { MinerPaymentComponent } from '../../containers/MinerPayment/MinerPayment.js'
import {
  fetchMinerPaymentTxSlate,
  getLatestMinerPayments,
  setPaymentMethodSetting,
  fetchMinerPaymentScript
} from '../actions/minerDataActions.js'

const mapStateToProps = (state) => ({
  isPaymentSettingProcessing: state.minerData.isPaymentSettingProcessing,
  isTxSlateLoading: state.minerData.isTxSlateLoading,
  paymentFormFeedback: state.minerData.paymentFormFeedback,
  minerPaymentTxSlate: state.minerData.minerPaymentTxSlate,
  paymentMethod: state.minerData.paymentData.method,
  payoutScript: state.minerData.payoutScript
})

const mapDispatchToProps = (dispatch) => {
  return {
    fetchMinerPaymentTxSlate: () => dispatch(fetchMinerPaymentTxSlate()),
    getLatestMinerPayments: () => dispatch(getLatestMinerPayments()),
    setPaymentMethodSetting: (state: any) => dispatch(setPaymentMethodSetting(state)),
    fetchMinerPaymentScript: () => dispatch(fetchMinerPaymentScript())
  }
}

export const MinerPaymentConnector = connect(mapStateToProps, mapDispatchToProps)(MinerPaymentComponent)
