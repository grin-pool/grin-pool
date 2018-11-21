import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'
import { GrinPoolDataConnector } from '../../redux/connectors/GrinPoolDataConnector.js'
import { GrinPoolSharesSubmittedConnector } from '../../redux/connectors/GrinPoolSharesSubmittedConnector.js'

export class GrinPoolDetailsComponent extends Component {
  UNSAFE_componentWillMount () {

  }

  fetchGrinPoolData = () => {

  }

  render () {
    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>GrinPool Details</h3>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody>
                <GrinPoolDataConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody>
                <GrinPoolSharesSubmittedConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
