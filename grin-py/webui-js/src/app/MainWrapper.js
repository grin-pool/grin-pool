import React, { PureComponent } from 'react'
import { getLatestBlock } from '../redux/actions/networkDataActions.js'
import { connect } from 'react-redux'

class MainWrapperComponent extends PureComponent {
  constructor (props) {
    super(props)
    const { getLatestBlock } = this.props
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
    getLatestBlock: () => dispatch(getLatestBlock())
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainWrapperComponent)
