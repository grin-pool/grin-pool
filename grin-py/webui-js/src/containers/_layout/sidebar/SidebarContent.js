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

  render () {
    return (
      <div className='sidebar__content'>
        <SidebarLink title='Home' route='/' icon='home' />
        <SidebarLink title='Pool' route='/pool' icon='chart-bars' />
        <SidebarLink title='Miner Stats' route='/miner' icon="screen" />
        <SidebarLink title='Payments' route='/miner/payment' icon="thumbs-up" />
        <SidebarLink title='About' route='/about' icon='file-empty' />
        <li className='sidebar__link'>
          <span className={`sidebar__link-icon lnr lnr-code`}/>
          <p className='sidebar__link-title'>
            <a href={'https://github.com/grin-pool/grin-pool'} style={{ color: 'inherit' }}>GitHub</a>
          </p>
        </li>
      </div>
    )
  }
}

const mapStateToProps = (state) => ({
})

const mapDispatchToProps = (dispatch) => ({

})

export const SidebarContentConnector = connect(mapStateToProps, mapDispatchToProps)(SidebarContent)
