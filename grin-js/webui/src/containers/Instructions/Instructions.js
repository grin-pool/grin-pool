import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'
import ReactGA from 'react-ga'

export class TutorialsComponent extends Component {
  constructor (props) {
    super(props)
    ReactGA.initialize('UA-132063819-1')
    ReactGA.pageview(window.location.pathname + window.location.search)
  }

  render () {
    return (
      <Container className='dashboard instructions'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Tutorials</h3>
          </Col>
        </Row>
        <Card>
          <CardBody>
            <Row>
              <Col xs={12} md={12} lg={8} xl={8}>
                <h4>How to Mine GRIN Tutorials</h4>
                <p>Some Tutorial</p>
              </Col>
            </Row>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Row>
              <Col xs={12} md={12} lg={10} xl={10}>
                <h4>How to Configure Pool Payouts</h4>
                <p>Some Instructions</p>
              </Col>
            </Row>
          </CardBody>
        </Card>
      </Container>
    )
  }
}
