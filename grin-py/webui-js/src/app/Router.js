import React from 'react'
import { Route, Switch } from 'react-router-dom'
import Layout from '../containers/_layout/Layout'
import MainWrapper from './MainWrapper'

import LogIn from '../containers/log_in/LogIn'
import ExamplePageOne from '../containers/example/ExamplePageOne'
import ExamplePageTwo from '../containers/example_two/ExamplePageTwo'
import { HomepageConnector } from '../redux/connectors/HomepageConnector.js'

const Router = () => (
  <MainWrapper>
    <main>
      <Switch>
        <Route exact path='/log_in' component={LogIn}/>
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
    </div>
  </div>
)

const Pages = () => (
  <Switch>
    <Route exact path='/' component={HomepageConnector}/>
    <Route path='/pages/one' component={ExamplePageOne}/>
    <Route path='/pages/two' component={ExamplePageTwo}/>
  </Switch>
)

export default Router
