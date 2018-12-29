import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'
import TopbarSidebarButton from './TopbarSidebarButton'
import { TopbarProfileConnector } from './TopbarProfile'
import { POOL_NAME } from '../../../custom/custom.js'

export default class Topbar extends PureComponent {
  render () {
    return (
      <div className='topbar'>
        <div className='topbar__wrapper'>
          <TopbarSidebarButton/>
          <Link className='topbar__logo' to='/'>
            <span>{POOL_NAME}</span>
          </Link>
          <div className='topbar__right'>
            <TopbarProfileConnector/>
          </div>
        </div>
      </div>
    )
  }
}
