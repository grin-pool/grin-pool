import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import SidebarLink from './SidebarLink'
import SidebarCategory from './SidebarCategory'
import { changeThemeToDark, changeThemeToLight } from '../../../redux/actions/themeActions'

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
        <SidebarCategory title="Miner" icon="screen">
          <SidebarLink title='Stats' route='/miner' />
          <SidebarLink title='Payment' route='/miner/payment' />
        </SidebarCategory>
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
  changeThemeToDark: () => dispatch(changeThemeToDark()),
  changeThemeToLight: () => dispatch(changeThemeToLight())
})

export const SidebarContentConnector = connect(mapStateToProps, mapDispatchToProps)(SidebarContent)
