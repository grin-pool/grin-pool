import React, { Component } from 'react'
import { Col, Container, Row } from 'reactstrap'

export class MinerComponent extends Component {
  UNSAFE_componentWillMount () {

  }

  fetchGrinPoolData = () => {

  }

  render () {
    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Miner Details</h3>
          </Col>
        </Row>
      </Container>
    )
  }
}
