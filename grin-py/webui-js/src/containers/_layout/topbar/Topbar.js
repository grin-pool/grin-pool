import React, { PureComponent } from 'react'
import { Link } from 'react-router-dom'
import TopbarSidebarButton from './TopbarSidebarButton'
import { TopbarProfileConnector } from './TopbarProfile'

export default class Topbar extends PureComponent {
  render () {
    return (
      <div className='topbar'>
        <div className='topbar__wrapper'>
          <TopbarSidebarButton/>
          <Link className='topbar__logo' to='/'>
            <span>MWGrinPool</span>FlooNet2
          </Link>
          <div className='topbar__right'>
            <TopbarProfileConnector/>
          </div>
        </div>
      </div>
    )
  }
}
