import React, { PureComponent } from 'react'
import { changeSidebarVisibility, changeMobileSidebarVisibility } from '../../../redux/actions/sidebarActions'
import { connect } from 'react-redux'

const icon = process.env.PUBLIC_URL + '/img/burger.svg'

class TopbarSidebarButton extends PureComponent {
  changeSidebarVisibility = () => {
    this.props.dispatch(changeSidebarVisibility())
  };

  changeMobileSidebarVisibility = () => {
    this.props.dispatch(changeMobileSidebarVisibility())
  };

  render () {
    return (
      <div>
        <button className='topbar__button topbar__button--desktop' onClick={this.changeSidebarVisibility}>
          <img src={icon} alt='' className='topbar__button-icon'/>
        </button>
        <button className='topbar__button topbar__button--mobile' onClick={this.changeMobileSidebarVisibility}>
          <img src={icon} alt='' className='topbar__button-icon'/>
        </button>
      </div>
    )
  }
}

const mapStateToProps = (state) => {
  return {
    sidebar: state.sidebar
  }
}

export default connect(mapStateToProps)(TopbarSidebarButton)
