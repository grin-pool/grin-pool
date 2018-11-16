import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Route, Switch, Redirect } from 'react-router-dom'
import Layout from '../containers/_layout/Layout'
import MainWrapper from './MainWrapper'
import { MinerConnector } from '../redux/connectors/MinerConnector.js'
import { HomepageConnector } from '../redux/connectors/HomepageConnector.js'
import { AboutComponent } from '../containers/About/About.js'
import { GrinPoolDetailsConnector } from '../redux/connectors/GrinPoolDetailsConnector.js'
import { LoginConnector } from '../redux/connectors/LoginConnector.js'

class Router extends Component {
  render () {
    return (
      <MainWrapper>
        <main>
          <Switch>
            <Route path='/' component={WrappedRoutesConnector}/>
          </Switch>
        </main>
      </MainWrapper>
    )
  }
}

class WrappedRoutes extends Component {
  render () {
    return (
      <div>
        <Layout/>
        <div className='container__wrap'>
          <Route exact path='/' component={HomepageConnector}/>
          <Route path='/pages' component={Pages}/>
          <Route path='/about' component={AboutComponent}/>
          <Route path='/pool' component={GrinPoolDetailsConnector} />
          <Route path="/login" component={LoginConnector} />
          <PrivateRoute path="/miner" component={MinerConnector} account={this.props.account} />
        </div>
      </div>
    )
  }
}

export const WrappedRoutesConnector = connect((state) => ({
  account: state.auth.account
}))(WrappedRoutes)

const Pages = () => (
  <Switch>
    <Route exact path='/' component={HomepageConnector}/>
  </Switch>
)

function PrivateRoute ({ component: Component, ...rest }) {
  return (
    <Route
      {...rest}
      render={props =>
        props.account ? (
          <Component {...props} />
        ) : (
          <Redirect
            to={{
              pathname: '/login',
              state: { from: props.location }
            }}
          />
        )
      }
    />
  )
}

export default Router
