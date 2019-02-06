import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'
import { GrinPoolDataConnector } from '../../redux/connectors/GrinPoolDataConnector.js'
import { GrinPoolSharesSubmittedConnector } from '../../redux/connectors/GrinPoolSharesSubmittedConnector.js'
import { GrinPoolStatsTableConnector } from '../../redux/connectors/GrinPoolStatsTableConnector.js'
import { GrinPoolRecentBlocksConnector } from '../../redux/connectors/GrinPoolRecentBlocksConnector.js'
import ReactGA from 'react-ga'

export class GrinPoolDetailsComponent extends Component {
  constructor (props) {
    super(props)
    ReactGA.initialize('UA-132063819-1')
    ReactGA.pageview(window.location.pathname + window.location.search)
  }

  UNSAFE_componentWillMount () {

  }

  fetchGrinPoolData = () => {

  }

  render () {
    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>BitGrinPool Details</h3>
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
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody>
                <GrinPoolStatsTableConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody>
                <GrinPoolRecentBlocksConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
