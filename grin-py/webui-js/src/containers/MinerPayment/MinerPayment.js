import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody, Form, FormGroup, Label, Input } from 'reactstrap'
import { MinerPaymentDataConnector } from '../../redux/connectors/MinerPaymentDataConnector.js'

export class MinerPaymentComponent extends Component {
  constructor (props) {
    super(props)
    this.state = {
      paymentType: 'manual'
    }
  }

  onPaymentTypeChange = (event) => {
    this.setState({
      paymentType: event.target.value
    })
  }

  renderManualPayoutOptions = () => {
    return (
      <Col sm={10}>
        <FormGroup check>
          <Label check>
            <Input type='radio' name='paymentMethod' />Online Wallet / Port
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input type='radio' name='paymentMethod' />Form Entry
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input type='radio' name='paymentMethod' disabled />GrinBox (Coming Soon)
          </Label>
        </FormGroup>
      </Col>
    )
  }

  renderAutomaticPayoutOptions = () => {
    return (
      <Col sm={10}>
        <FormGroup check>
          <p>This content to be added soon!</p>
        </FormGroup>
      </Col>
    )
  }

  render () {
    // const { username } = this.props
    const { paymentType } = this.state
    return (
      <Container className='dashboard'>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Miner Payment</h3>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={6} xl={6}>
            <Card>
              <CardBody>
                <h4>Payout</h4>
                <p>GrinPool supports multiple methods of payment, including automatic payments and manual / on-demand payments. The list of payment methods is likely to grow, so stay tuned!</p>
                <br />
                <Form className='minerPaymentForm'>
                  <FormGroup>
                    <Label for='paymentType'>Payment Type:</Label>
                    <Input type='select' name='paymentType' id='paymentSelect' onChange={this.onPaymentTypeChange}>
                      <option>------------</option>
                      <option value='scheduled'>Scheduled Payout</option>
                      <option value='manual'>Manual Payout</option>
                    </Input>
                  </FormGroup>
                  <FormGroup tag='fieldset' row>
                    <legend className='col-form-label'>Payment Method:</legend>
                    {paymentType === 'manual' ? this.renderManualPayoutOptions() : this.renderAutomaticPayoutOptions()}
                  </FormGroup>
                </Form>
              </CardBody>
            </Card>
          </Col>
          <Col xs={12} md={12} lg={6} xl={6}>
            <Card>
              <CardBody>
                <MinerPaymentDataConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
