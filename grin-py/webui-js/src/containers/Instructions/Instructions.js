import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'

export class InstructionsComponent extends Component {
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
              <p>To learn how to properly inititate pool payments, please read our tutorial <a href='https://medium.com/@blade.doyle/gpu-mining-on-mwgrinpool-com-how-to-72970e550a27' rel='noopener noreferrer' target='_blank'>here</a></p>
            </CardBody>
          </Card>
        </Row>
      </Container>
    )
  }
}
