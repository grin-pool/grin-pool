
import { connect } from 'react-redux'
import { GrinPoolSharesSubmittedComponent } from '../../containers/GrinPoolData/GrinPoolSharesSubmitted.js'
import { fetchGrinPoolSharesSubmitted } from '../actions/grinPoolDataActions.js'

const mapStateToProps = (state) => {
  return {
    sharesSubmitted: state.grinPoolData.sharesSubmitted
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    fetchGrinPoolSharesSubmitted: () => dispatch(fetchGrinPoolSharesSubmitted())
  }
}

export const GrinPoolSharesSubmittedConnector = connect(mapStateToProps, mapDispatchToProps)(GrinPoolSharesSubmittedComponent)
