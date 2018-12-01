import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody, Form, FormGroup, Label, Input } from 'reactstrap'
import { MinerPaymentDataConnector } from '../../redux/connectors/MinerPaymentDataConnector.js'

export class MinerPaymentComponent extends Component {
  constructor (props) {
    super(props)
    this.state = {
      paymentType: 'manual',
      manualPaymentMethod: ''
    }
  }

  onPaymentTypeChange = (event) => {
    this.setState({
      paymentType: event.target.value
    })
  }

  onManualPaymentMethodChange = (event) => {
    this.setState({
      manualPaymentMethod: event.target.value
    })
  }

  renderManualPayoutOptions = () => {
    return (
      <Col sm={10}>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onManualPaymentMethodChange} type='radio' value='onlineWallet' name='paymentMethod' />Online Wallet / Port
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onManualPaymentMethodChange} type='radio' value='cutAndPaste' name='paymentMethod' />Payout Cut &amp; Paste
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onManualPaymentMethodChange} type='radio' value='downloadScript' name='paymentMethod' />Download Payment Request Script
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

  renderPayoutForm = () => {
    const { manualPaymentMethod } = this.state
    switch (manualPaymentMethod) {
      case 'onlineWallet':
        return (
          <div>
            <Label for="onlineWallet">Enter Wallet &amp; Port:</Label>
            <Input
              onChange={this.onChangeOnlineWallet}
              type="text"
              name="onlineWallet"
              id="onlineWallet"
              placeholder="ex http://195.128.200.15:13415"
              className='form-control' />
          </div>
        )
      case 'cutAndPaste':
        return (
          <div>
            <Label for="cutAndPaste">Copy and Paste the Following Code:</Label><br />
            <span style={{ fontFamily: 'Courier' }}>
              Blah blajfajlsfd;ljasdl;fjasdjf<br />
              asdlfj;lasdjflas;fjas;d<br />
              klasdfjlasjdf;ladfjsj Test<br />
            </span>
          </div>
        )
      case 'downloadScript':
        return (
          <div>
            <Label for="downloadScript">Download the Script and Upload to Wallet:</Label><br />
            <a href=''>Click Me</a>
          </div>
        )
    }
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
                  <FormGroup tag='fieldset' row>
                    {this.renderPayoutForm()}
                  </FormGroup>
                  <div style={{ textAlign: 'center' }}>
                    <button className="btn btn-outline-primary account__btn account__btn--small">{'Clear'}</button>
                    <button className="btn btn-primary account__btn account__btn--small">{'Submit'}</button>
                  </div>
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
