import React, { PureComponent } from 'react'
import { getLatestBlock } from '../redux/actions/networkDataActions.js'
import { attemptAutoLoginFromCookies } from '../redux/actions/authActions.js'
import { connect } from 'react-redux'

class MainWrapperComponent extends PureComponent {
  constructor (props) {
    super(props)
    const { getLatestBlock, attemptAutoLoginFromCookies } = this.props
    attemptAutoLoginFromCookies()
    getLatestBlock()
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
    getLatestBlock: () => dispatch(getLatestBlock())
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainWrapperComponent)
