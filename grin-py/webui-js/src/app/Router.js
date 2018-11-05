import React from 'react'
import { Route, Switch } from 'react-router-dom'
import Layout from '../containers/_layout/Layout'
import MainWrapper from './MainWrapper'

import LogIn from '../containers/log_in/LogIn'
import { HomepageConnector } from '../redux/connectors/HomepageConnector.js'
import { AboutComponent } from '../containers/About/About.js'
import { GrinPoolDetailsConnector } from '../redux/connectors/GrinPoolDetailsConnector.js'

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
      <Route path='/about' component={AboutComponent}/>
      <Route path='/pool' component={GrinPoolDetailsConnector} />
    </div>
  </div>
)

const Pages = () => (
  <Switch>
    <Route exact path='/' component={HomepageConnector}/>
  </Switch>
)

export default Router
