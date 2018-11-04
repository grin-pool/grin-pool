import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { Badge } from 'reactstrap'
import { NavLink, withRouter } from 'react-router-dom'

class SidebarLink extends PureComponent {
  static propTypes = {
    title: PropTypes.string.isRequired,
    icon: PropTypes.string,
    new: PropTypes.bool,
    route: PropTypes.string
  };

  render () {
    return (
      <NavLink to={this.props.route ? this.props.route : '/'} onClick={this.props.onClick}
        activeClassName='sidebar__link-active'>
        <li className='sidebar__link'>
          {this.props.icon ? <span className={`sidebar__link-icon lnr lnr-${this.props.icon}`}/> : ''}
          {this.props.route.includes('http') ? (
            <p className='sidebar__link-title'>
              <a href={this.props.route} style={{ color: 'inherit' }}>{this.props.title}</a>
              {this.props.new ? <Badge className='sidebar__link-badge'><span>New</span></Badge> : ''}
            </p>
          ) : (
            <p className='sidebar__link-title'>
              {this.props.title}
              {this.props.new ? <Badge className='sidebar__link-badge'><span>New</span></Badge> : ''}
            </p>
          )}
        </li>
      </NavLink>
    )
  }
}

export default withRouter(SidebarLink)
