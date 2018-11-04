import React from 'react'
import App from './app/App'
import { render } from 'react-dom'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import store from './app/store'
import ScrollToTop from './app/ScrollToTop'

render(
  <Provider store={store}>
    <BrowserRouter basename='http://localhost:5000/'>
      <ScrollToTop>
        <App/>
      </ScrollToTop>
    </BrowserRouter>
  </Provider>,
  document.getElementById('root')
)
