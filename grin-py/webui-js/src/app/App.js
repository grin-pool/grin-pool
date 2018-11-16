import React, { Component } from 'react'
import 'bootstrap/dist/css/bootstrap.css'
import '../scss/app.scss'
import Router from './Router'
import { library } from '@fortawesome/fontawesome-svg-core'
import { faChartLine, faClock, faDollarSign, faLink, faDesktop } from '@fortawesome/free-solid-svg-icons'

library.add(faChartLine)
library.add(faClock)
library.add(faDollarSign)
library.add(faLink)
library.add(faDesktop)

class App extends Component {
  constructor () {
    super()
    this.state = {
      loading: true,
      loaded: false
    }
  }

  componentDidMount () {
    window.addEventListener('load', () => {
      this.setState({ loading: false })
      setTimeout(() => this.setState({ loaded: true }), 500)
    })
  }

  render () {
    const loaded = this.state.loaded
    return (
      <div>
        {!loaded && <div className={`load${this.state.loading ? '' : ' loaded'}`}>
          <div className='load__icon-wrap'>
            <svg className='load__icon'>
              <path fill='#4ce1b6' d='M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z'/>
            </svg>
          </div>
        </div>}
        <div>
          <Router account={this.props.account} />
        </div>
      </div>
    )
  }
}

export default App
