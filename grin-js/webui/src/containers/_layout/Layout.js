import React, { PureComponent } from 'react'
import Topbar from './topbar/Topbar'
import Sidebar from './sidebar/Sidebar'

export default class Layout extends PureComponent {
  render () {
    return (
      <div>
        <Topbar/>
        <Sidebar/>
      </div>
    )
  }
}
