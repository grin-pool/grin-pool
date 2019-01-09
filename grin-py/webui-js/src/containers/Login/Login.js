import React from 'react'
import { Redirect } from 'react-router-dom'
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
      password: ''
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
    const { login } = this.props
    login(this.state.username, this.state.password)
  }

  register = (e) => {
    e.preventDefault()
    const { createUser } = this.props
    createUser(this.state.username, this.state.password)
  }

  renderSpinner = () => {
    return <Spinner name='circle' color='white' fadeIn='none' style={{ marginLeft: 'auto', marginRight: 'auto', height: 21 }} />
  }

  render () {
    const { isCreatingAccount, isLoggingIn } = this.props
    const { from } = this.props.location.state || { from: { pathname: '/' } }
    const { redirectToReferrer } = this.state
    if (redirectToReferrer) return <Redirect to={from} />

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
                <Form className='login-form'>
                  <FormGroup>
                    <Label for="loginEmail">Username:</Label>
                    <Input onChange={this.onChangeUsername} type="email" name="email" id="loginEmail" placeholder="" />
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
                  <div style={{ textAlign: 'center' }}>
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
