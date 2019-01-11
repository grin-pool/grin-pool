import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'
import { NetworkDataConnector } from '../../redux/connectors/NetworkDataConnector.js'
import { GrinPoolDataConnector } from '../../redux/connectors/GrinPoolDataConnector.js'
import { NetworkRecentBlocksConnector } from '../../redux/connectors/NetworkRecentBlocksConnector.js'
import ReactGA from 'react-ga'

export class HomepageComponent extends Component {
  constructor (props) {
    super(props)
    ReactGA.initialize('UA-132063819-1')
    ReactGA.pageview(window.location.pathname + window.location.search)
  }

  render () {
    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Dashboard</h3>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody>
                <NetworkDataConnector />
              </CardBody>
            </Card>
          </Col>
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
                <NetworkRecentBlocksConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
