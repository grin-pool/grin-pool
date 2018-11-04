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
        <SidebarLink title='Pool' route='/pages/one' icon='chart-bars' />
        <SidebarLink title='Miner' route='/pages/one' icon='screen' />
        <SidebarLink title='About' route='/pages/one' icon='file-empty' />
        <SidebarLink title='GitHub' route='/pages/one' icon='code' />

        <ul className='sidebar__block'>
          <SidebarCategory title='Layout' icon='layers'>
            <li className='sidebar__link' onClick={this.changeToLight}>
              <p className='sidebar__link-title'>Light Theme</p>
            </li>
            <li className='sidebar__link' onClick={this.changeToDark}>
              <p className='sidebar__link-title'>Dark Theme</p>
            </li>
          </SidebarCategory>
        </ul>
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
