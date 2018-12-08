import React, { PureComponent } from 'react'
import { getLatestBlock } from '../redux/actions/networkDataActions.js'
import { attemptAutoLoginFromCookies } from '../redux/actions/authActions.js'
import { fetchGrinPoolBlocksMined } from '../redux/actions/grinPoolDataActions.js'
import { connect } from 'react-redux'

class MainWrapperComponent extends PureComponent {
  constructor (props) {
    super(props)
    const { getLatestBlock, attemptAutoLoginFromCookies, fetchGrinPoolBlocksMined } = this.props
    attemptAutoLoginFromCookies()
    getLatestBlock()
    fetchGrinPoolBlocksMined()
    setInterval(getLatestBlock, 10000)
  }
  render () {
    const theme = this.props.theme.className
    return (
      <div className={theme}>
        <div className={this.props.sidebar.collapse ? 'wrapper wrapper--full-width' : 'wrapper'}>
          {this.props.children}
        </div>
      </div>
    )
  }
}

const mapStateToProps = (state) => {
  return {
    theme: state.theme,
    sidebar: state.sidebar
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    attemptAutoLoginFromCookies: () => dispatch(attemptAutoLoginFromCookies()),
    getLatestBlock: () => dispatch(getLatestBlock()),
    fetchGrinPoolBlocksMined: () => dispatch(fetchGrinPoolBlocksMined())
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainWrapperComponent)
