import React, { PureComponent } from 'react'
import { Collapse } from 'reactstrap'
import { Link } from 'react-router-dom'
import NotificationsIcon from 'mdi-react/NotificationsIcon'

const notifications = []

export default class TopbarNotification extends PureComponent {
  constructor (props) {
    super(props)
    this.state = {
      collapse: false
    }
    this.toggle = this.toggle.bind(this)
  }

  toggle () {
    this.setState({ collapse: !this.state.collapse })
  }

  render () {
    return (
      <div className='topbar__collapse'>
        <button className='topbar__btn' onClick={this.toggle}>
          <NotificationsIcon/>
        </button>
        {this.state.collapse && <div className='topbar__back' onClick={this.toggle}/>}
        <Collapse
          isOpen={this.state.collapse}
          className='topbar__collapse-content'
        >
          <div className='topbar__collapse-title-wrap'>
            <p className='topbar__collapse-title'>Notifications</p>
            <button className='topbar__collapse-button'>Mark all as read</button>
          </div>
          {notifications.map((notification) => (
            <div className='topbar__collapse-item' key={notification.name}>
              <div className='topbar__collapse-img-wrap'>
                <img className='topbar__collapse-img' src={notification.ava} alt=''/>
              </div>
              <p className='topbar__collapse-message'>
                <span className='topbar__collapse-name'>{notification.name}</span>
                {notification.message}
              </p>
              <p className='topbar__collapse-date'>{notification.date}</p>
            </div>
          ))}
          <Link className='topbar__collapse-link' to='/dashboard_default'>
            See all notifications
          </Link>
        </Collapse>
      </div>
    )
  }
}
