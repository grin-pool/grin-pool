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
        <ul className='sidebar__block'>
          <SidebarCategory title='Example Pages' icon='diamond'>
            <SidebarLink title='Page one' route='/pages/one' onClick={this.hideSidebar}/>
            <SidebarLink title='Page two' route='/pages/two' onClick={this.hideSidebar}/>
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
