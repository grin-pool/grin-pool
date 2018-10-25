import React, { PureComponent } from 'react'
import { Card, CardBody, Col } from 'reactstrap'

export default class ExampleCard extends PureComponent {
  render () {
    return (
      <Col md={12}>
        <Card>
          <CardBody>
            <div className='card__title'>
              <h5 className='bold-text'>Example title</h5>
              <h5 className='subhead'>Example subhead</h5>
            </div>
            <p>
              Your content here
            </p>
          </CardBody>
        </Card>
      </Col>
    )
  }
}
