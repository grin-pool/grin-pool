import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody, Form, FormGroup, Label, Input, Alert } from 'reactstrap'
import { MinerPaymentDataConnector } from '../../redux/connectors/MinerPaymentDataConnector.js'
import Blob from 'blob'
import Spinner from 'react-spinkit'

export class MinerPaymentComponent extends Component {
  constructor (props) {
    super(props)
    this.state = {
      paymentType: '',
      manualPaymentMethod: ''
    }
  }

  renderSpinner = (height) => {
    return <Spinner name='circle' color='white' fadeIn='none' style={{ marginLeft: 'auto', marginRight: 'auto', height }} />
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

  _downloadTxtFile = () => {
    const { minerPaymentTxSlate } = this.props
    const element = document.createElement('a')
    const file = new Blob([minerPaymentTxSlate], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    const date = new Date()
    const timestamp = Math.floor(date.getTime() / 1000)
    element.download = `payoutScript-${timestamp}.txt`
    element.click()
  }

  componentDidMount = () => {
    const { fetchMinerPaymentTxSlate, getLatestMinerPayments } = this.props
    getLatestMinerPayments()
    fetchMinerPaymentTxSlate()
  }

  renderManualPayoutOptions = () => {
    return (
      <Col sm={10}>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onManualPaymentMethodChange} type='radio' value='http' name='paymentMethod' />Online Wallet / Port
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onManualPaymentMethodChange} type='radio' value='payoutScript' name='paymentMethod' />Download Payment Request Script
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
    const { isPayoutScriptLoading } = this.props
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
      case 'payoutScript':
        return (
          <div style={{ textAlign: 'center' }}>
            <Label for="payoutScript">Download the Script and Upload to Wallet:</Label><br />
            {isPayoutScriptLoading ? (
              this.renderSpinner('1.8em')
            ) : (
              <a href='' onClick={this._downloadTxtFile} style={{ fontWeight: 'bold' }}>Download</a>
            )}
          </div>
        )
    }
  }

  onSubmit = (e) => {
    e.preventDefault()
    const { manualPaymentMethod } = this.state
    const { setPaymentMethodSetting } = this.props
    setPaymentMethodSetting('method', manualPaymentMethod)
  }

  onClear = (e) => {
    e.preventDefault()
  }

  render () {
    const { paymentType } = this.state
    const { isPaymentSettingProcessing, paymentFormFeedback } = this.props
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
                    <button className="btn btn-outline-primary account__btn account__btn--small" onClick={this.onClear}>{'Clear'}</button>
                    <button className="btn btn-primary account__btn account__btn--small" style={{ width: '84px' }} onClick={this.onSubmit}>
                      {isPaymentSettingProcessing ? this.renderSpinner('21px') : 'Save'}
                    </button>
                  </div>
                  <div style={{ textAlign: 'center', marginTop: '10px' }}>
                    {paymentFormFeedback && <Alert style={{ display: 'inline' }} color={paymentFormFeedback.color}>{paymentFormFeedback.message}</Alert> }
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
