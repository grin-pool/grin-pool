import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

class MainWrapper extends PureComponent {
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

export default connect(state => {
  return { theme: state.theme,
    sidebar: state.sidebar }
})(MainWrapper)
