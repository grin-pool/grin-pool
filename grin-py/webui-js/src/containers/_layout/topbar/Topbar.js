import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'
import TopbarSidebarButton from './TopbarSidebarButton'
import { TopbarProfileConnector } from './TopbarProfile'
import TopbarMail from './TopbarMail'
import TopbarNotification from './TopbarNotification'
import TopbarSearch from './TopbarSearch'

export default class Topbar extends PureComponent {
  render () {
    return (
      <div className='topbar'>
        <div className='topbar__wrapper'>
          <TopbarSidebarButton/>
          <Link className='topbar__logo' to='/'/>
          <div className='topbar__right'>
            <TopbarSearch/>
            <TopbarNotification/>
            <TopbarMail new/>
            <TopbarProfileConnector/>
          </div>
        </div>
      </div>
    )
  }
}
