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
    setInterval(getLatestBlock, 30000)
  }

  render () {
    const theme = this.props.theme.className
    return (
      <div className={theme} id='fireworksContainer'>
        <audio id='fireworks' src="/fireworks.mp3" />
        <div className={this.props.sidebar.collapse ? 'wrapper wrapper--full-width' : 'wrapper'}>
          {this.props.children}
        </div>
      </div>
    )
  }
}

const mapStateToProps = (state) => {
  const c29Blocks = state.grinPoolData.poolBlocksMined.c29 || []
  const c31Blocks = state.grinPoolData.poolBlocksMined.c31 || []
  const cumulativeRecentPoolBlocks = [...c29Blocks, ...c31Blocks]
  return {
    theme: state.theme,
    sidebar: state.sidebar,
    cumulativeRecentPoolBlocks,
    recentPoolBlocks: state.grinPoolData.poolBlocksMined,
    latestBlockHeight: state.networkData.latestBlock.height || 0,
    c29Blocks,
    c31Blocks,
    isAudioEnabled: state.minerData.isAudioEnabled
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    attemptAutoLoginFromCookies: () => dispatch(attemptAutoLoginFromCookies()),
    getLatestBlock: () => dispatch(getLatestBlock())
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(MainWrapperComponent)
