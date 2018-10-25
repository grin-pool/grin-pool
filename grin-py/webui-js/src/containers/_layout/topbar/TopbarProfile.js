import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

import DownIcon from 'mdi-react/ChevronDownIcon'
import TopbarMenuLink from './TopbarMenuLink'
import { Collapse } from 'reactstrap'

const Ava = process.env.PUBLIC_URL + '/img/ava.png'

class TopbarProfile extends PureComponent {
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
    const { account } = this.props
    return (
      <div className='topbar__profile'>
        {account ? (
          <div className='topbar__avatar' onClick={this.toggle}>
            <img className='topbar__avatar-img' src={Ava} alt='avatar'/>
            <p className='topbar__avatar-name'>{account.username}</p>
            <DownIcon className='topbar__avatar-icon'/>
          </div>
        ) : (
          <div className='topbar__avatar'>
            <a className='topbar__avatar-name'>Log in</a>
          </div>
        )}
        {this.state.collapse && <div className='topbar__back' onClick={this.toggle}/>}
        <Collapse isOpen={this.state.collapse} className='topbar__menu-wrap'>
          <div className='topbar__menu'>
            <TopbarMenuLink title='Page One' icon='user' path='/pages/one'/>
            <TopbarMenuLink title='Page Two' icon='calendar-full' path='/pages/two'/>
            <div className='topbar__menu-divider'/>
            <TopbarMenuLink title='Log Out' icon='exit' path='/log_in'/>
          </div>
        </Collapse>
      </div>
    )
  }
}

const mapStateToProps = (state) => ({
  account: state.account
})

const mapDispatchToProps = (dispatch) => ({

})

export const TopbarProfileConnector = connect(mapStateToProps, mapDispatchToProps)(TopbarProfile)
