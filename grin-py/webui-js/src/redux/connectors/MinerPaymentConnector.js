
import { connect } from 'react-redux'
import { MinerPaymentComponent } from '../../containers/MinerPayment/MinerPayment.js'
import { fetchMinerPaymentTxSlate, getLatestMinerPayments, setPaymentMethodSetting } from '../actions/minerDataActions.js'

const mapStateToProps = (state) => ({
  // username: state.auth.account.username
  isPaymentSettingProcessing: state.minerData.isPaymentSettingProcessing,
  isPayoutScriptLoading: state.minerData.isPayoutScriptLoading,
  paymentFormFeedback: state.minerData.paymentFormFeedback,
  minerPaymentTxSlate: state.minerData.minerPaymentTxSlate
})

const mapDispatchToProps = (dispatch) => {
  return {
    fetchMinerPaymentTxSlate: () => dispatch(fetchMinerPaymentTxSlate()),
    getLatestMinerPayments: () => dispatch(getLatestMinerPayments()),
    setPaymentMethodSetting: (field: string, value: string) => dispatch(setPaymentMethodSetting(field, value))
  }
}

export const MinerPaymentConnector = connect(mapStateToProps, mapDispatchToProps)(MinerPaymentComponent)
