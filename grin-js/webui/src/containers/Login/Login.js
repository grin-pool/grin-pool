import React from 'react'
import { Redirect, NavLink } from 'react-router-dom'
import { Alert, Form, FormGroup, Label, Input, Row, Col, Container, Card, CardBody } from 'reactstrap'
import Spinner from 'react-spinkit'
import ReactGA from 'react-ga'

export class LoginComponent extends React.Component {
  state = { redirectToReferrer: false }
  constructor () {
    super()
    this.state = {
      showPassword: false,
      username: '',
      password: '',
      isCheckboxInvalid: null
    }
    ReactGA.initialize('UA-132063819-1')
    ReactGA.pageview(window.location.pathname + window.location.search)
  }

  showPassword = (e) => {
    e.preventDefault()
    this.setState({
      showPassword: !this.state.showPassword
    })
  }

  onChangePassword = (e) => {
    const password = e.target.value
    this.setState({
      password
    })
  }

  onChangeUsername = (e) => {
    const username = e.target.value
    this.setState({
      username
    })
  }

  login = (e) => {
    e.preventDefault()
    const { login, createAuthError } = this.props
    const { username, password } = this.state
    if (username.includes('.')) {
      createAuthError('Invalid username, please note that all periods (.) have been changed to underscores (_)')
      return
    }
    login(username, password)
  }

  register = (e) => {
    e.preventDefault()
    const { createUser, createAuthError } = this.props
    const { isCheckboxInvalid, username, password } = this.state
    if (username.includes('.')) {
      createAuthError('Usernames cannot include periods (.)')
      return
    }
    if (isCheckboxInvalid === true || isCheckboxInvalid === null) {
      this.setState({
        isCheckboxInvalid: true
      })
    } else {
      createUser(username, password)
    }
  }

  renderSpinner = () => {
    return <Spinner name='circle' color='white' fadeIn='none' style={{ marginLeft: 'auto', marginRight: 'auto', height: 21 }} />
  }

  onCheckboxChange = (e) => {
    const value = e.target.checked
    this.setState({
      isCheckboxInvalid: !value
    })
  }

  render () {
    const { isCreatingAccount, isLoggingIn } = this.props
    const { from } = this.props.location.state || { from: { pathname: '/' } }
    const { redirectToReferrer, isCheckboxInvalid } = this.state
    if (redirectToReferrer) return <Redirect to={from} />

    const redSyntax = isCheckboxInvalid ? 'red' : ''

    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Login or Register</h3>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={6} xl={6}>
            <Card>
              <CardBody>
                <div className="account__head">
                  <h3 className="account__title">Welcome to
                  <span className="account__logo"> Grin
                  <span className="account__logo-accent">Pool</span>
                  </span>
                  </h3>
                  <h4 className="account__subhead subhead">Start mining GRIN today</h4>
                </div>
                <Alert color='warning' style={{ textAlign: 'center', position: 'relative' }}>Please note that usernames that include a period (.) will soon have them replaced by an underscore (_). For example, a username "foo@bar.com" will be updated to "foo@bar_com"</Alert>
                <Form className='login-form'>
                  <FormGroup>
                    <Label for="loginEmail">Username:</Label>
                    <Input onChange={this.onChangeUsername} type="text" name="email" id="loginEmail" placeholder="" />
                  </FormGroup>
                  <FormGroup>
                    <Label for="loginPassword">Password:</Label>
                    <Input onChange={this.onChangePassword} type="password" name="password" id="loginPassword" placeholder="" />
                  </FormGroup>
                  <div>
                    {this.props.authError && (
                      <Alert color='danger' style={{ textAlign: 'center' }}>
                        {this.props.authError}
                      </Alert>
                    )}
                  </div>
                  <br />
                  <FormGroup check>
                    <Label for='terms-of-service' check>
                      <Input onChange={this.onCheckboxChange} className={`form-control`} style={{ height: '16px', width: '16px' }} type="checkbox" required />{'  '}<span className={redSyntax} >By checking this box you agree to the GrinPool <NavLink className={redSyntax} to='/terms-of-service'>Terms of Service</NavLink></span>
                    </Label>
                  </FormGroup>
                  <br />
                  <div style={{ textAlign: 'center' }} className={'login-form'}>
                    <button onClick={this.login} className="btn btn-primary account__btn account__btn--small">{(isLoggingIn && !isCreatingAccount) ? this.renderSpinner() : 'Sign In'}</button>
                    <button onClick={this.register} className="btn btn-outline-primary account__btn account__btn--small">{isCreatingAccount ? this.renderSpinner() : 'Create Account'}</button>
                  </div>
                </Form>
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
