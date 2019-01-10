import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'
import ReactGA from 'react-ga'

export class InstructionsComponent extends Component {
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
            <h1 className='page-title'>Instructions</h1>
          </Col>
        </Row>
        <Row>
          <Card>
            <CardBody>
              <h2>How to Mine Grin</h2>
              <p>To learn how to mine GRIN with one or more GPUs, please read our tutorial <a href='https://medium.com/@blade.doyle/gpu-mining-on-mwgrinpool-com-how-to-72970e550a27' rel='noopener noreferrer' target='_blank'>here</a></p>
            </CardBody>
          </Card>
        </Row>
        <Row>
          <Card>
            <CardBody>
              <h2>How to Configure Pool Payouts</h2>
              <p>To learn how to properly inititate pool payments, please read our tutorial <a href='https://medium.com/@blade.doyle/configure-payments-on-mwgrinpool-com-how-to-7b84163ec467' rel='noopener noreferrer' target='_blank'>here</a></p>
            </CardBody>
          </Card>
        </Row>
      </Container>
    )
  }
}
