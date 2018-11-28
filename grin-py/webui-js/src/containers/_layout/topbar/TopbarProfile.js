import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import DownIcon from 'mdi-react/ChevronDownIcon'
import TopbarMenuLink from './TopbarMenuLink'
import { Collapse } from 'reactstrap'
import { logout } from '../../../redux/actions/authActions.js'

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

  onClickLogout = () => {
    const { logout } = this.props
    this.setState({
      collapse: false
    })
    logout()
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
            <Link className='topbar__avatar-name' to='/login'>Log in</Link>
          </div>
        )}
        {this.state.collapse && <div className='topbar__back' onClick={this.toggle}/>}
        <Collapse isOpen={this.state.collapse} className='topbar__menu-wrap'>
          <div className='topbar__menu'>
            <TopbarMenuLink title='Stats' path='/miner'/>
            <TopbarMenuLink title='Payment' path='/miner/payment'/>
            <div className='topbar__menu-divider'/>
            <Link className='topbar__link' to='/login' onClick={this.onClickLogout}>
              <span className={`topbar__link-icon lnr lnr-exit`}/>
              <p className='topbar__link-title'>Logout</p>
            </Link>
          </div>
        </Collapse>
      </div>
    )
  }
}

const mapStateToProps = (state) => ({
  account: state.auth.account
})

const mapDispatchToProps = (dispatch) => ({
  logout: () => dispatch(logout())
})

export const TopbarProfileConnector = connect(mapStateToProps, mapDispatchToProps)(TopbarProfile)
