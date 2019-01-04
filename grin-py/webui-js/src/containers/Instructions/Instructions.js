import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'

export class InstructionsComponent extends Component {
  render () {
    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Instructions</h3>
          </Col>
        </Row>
        <Row>
          <Card>
            <CardBody>
              <p>Yay</p>
            </CardBody>
          </Card>
        </Row>
      </Container>
    )
  }
}
