import React, { Component } from 'react'
import { Col, Card, CardBody } from 'reactstrap'

export class AboutComponent extends Component {
  render () {
    return (
      <Col>
        <Card>
          <CardBody>
            <div className='card__title'>
              <h5 className='bold-text'>Open-Source Mining Pool for the MimbleWimble Grin Blockchain</h5>
            </div>
            <h4 className='bold-text'>About GrinPool</h4>
            <p>Under Construction...</p>
          </CardBody>
        </Card>
      </Col>
    )
  }
}
