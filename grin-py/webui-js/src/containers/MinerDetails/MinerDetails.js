import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody } from 'reactstrap'
import { MinerDataConnector } from '../../redux/connectors/MinerDataConnector.js'

export class MinerDetailsComponent extends Component {
  UNSAFE_componentWillMount () {

  }

  fetchGrinPoolData = () => {

  }

  render () {
    const { username } = this.props
    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>{username} Miner Details</h3>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody>
                <MinerDataConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
