import React from 'react'
import { Route, Switch, Redirect } from 'react-router-dom'
import Layout from '../containers/_layout/Layout'
import MainWrapper from './MainWrapper'
import { MinerConnector } from '../redux/connectors/MinerConnector.js'
import { HomepageConnector } from '../redux/connectors/HomepageConnector.js'
import { AboutComponent } from '../containers/About/About.js'
import { GrinPoolDetailsConnector } from '../redux/connectors/GrinPoolDetailsConnector.js'
import { LoginConnector } from '../redux/connectors/LoginConnector.js'

const Router = () => (
  <MainWrapper>
    <main>
      <Switch>
        <Route path='/' component={wrappedRoutes}/>
      </Switch>
    </main>
  </MainWrapper>
)

const wrappedRoutes = () => (
  <div>
    <Layout/>
    <div className='container__wrap'>
      <Route exact path='/' component={HomepageConnector}/>
      <Route path='/pages' component={Pages}/>
      <Route path='/about' component={AboutComponent}/>
      <Route path='/pool' component={GrinPoolDetailsConnector} />
      <Route path="/login" component={LoginConnector} />
      <PrivateRoute path="/miner" component={MinerConnector} />
    </div>
  </div>
)

const Pages = () => (
  <Switch>
    <Route exact path='/' component={HomepageConnector}/>
  </Switch>
)

const fakeAuth = {
  isAuthenticated: false,
  authenticate (cb) {
    this.isAuthenticated = true
    setTimeout(cb, 100) // fake async
  },
  signout (cb) {
    this.isAuthenticated = false
    setTimeout(cb, 100)
  }
}

function PrivateRoute ({ component: Component, ...rest }) {
  return (
    <Route
      {...rest}
      render={props =>
        fakeAuth.isAuthenticated ? (
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
