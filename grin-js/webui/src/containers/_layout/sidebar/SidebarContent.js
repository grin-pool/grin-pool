import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import SidebarLink from './SidebarLink'

class SidebarContent extends PureComponent {
  changeToDark = () => {
    this.props.changeThemeToDark()
    this.hideSidebar()
  };

  changeToLight = () => {
    this.props.changeThemeToLight()
    this.hideSidebar()
  };

  hideSidebar = () => {
    this.props.onClick()
  };

  toggleAudioEnabled = () => {
    const { toggleAudioEnabled } = this.props
    toggleAudioEnabled()
  }

  render () {
    const { isAudioEnabled } = this.props
    return (
      <div className='sidebar__content'>
        <SidebarLink title='Home' route='/' icon='home' />
        <SidebarLink title='Pool' route='/pool' icon='chart-bars' />
        <SidebarLink title='Miner Stats' route='/miner' icon="screen" />
        <SidebarLink title='Rig Stats' route='/rigs' icon="screen" />
        <SidebarLink title='Payments' route='/miner/payment' icon="thumbs-up" />
        <SidebarLink title='Getting Started &amp; FAQ' route='/info' icon='file-empty' />
        <li className='sidebar__link'>
          <span className={`sidebar__link-icon lnr lnr-code`}/>
          <p className='sidebar__link-title'>
            <a href={'https://github.com/grin-pool/grin-pool'} style={{ color: 'inherit' }}>GitHub</a>
          </p>
        </li>
        <li className='sidebar__link' onClick={this.toggleAudioEnabled}>
          <span style={{ cursor: 'pointer' }} className={isAudioEnabled ? 'lnr lnr-volume-high' : 'lnr lnr-volume'} />
        </li>
      </div>
    )
  }
}

const mapStateToProps = (state) => ({
  isAudioEnabled: state.minerData.isAudioEnabled
})

const mapDispatchToProps = (dispatch) => ({
  toggleAudioEnabled: () => dispatch({ type: 'IS_AUDIO_ENABLED' })
})

export const SidebarContentConnector = connect(mapStateToProps, mapDispatchToProps)(SidebarContent)
