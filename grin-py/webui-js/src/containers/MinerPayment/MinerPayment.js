import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody, Form, FormGroup, Label, Input, Alert } from 'reactstrap'
import { MinerPaymentDataConnector } from '../../redux/connectors/MinerPaymentDataConnector.js'
import { LatestMinerPaymentsConnector } from '../../redux/connectors/LatestMinerPaymentsConnector.js'
import Blob from 'blob'
import Spinner from 'react-spinkit'

export class MinerPaymentComponent extends Component {
  constructor (props) {
    super(props)
    const { paymentMethod, paymentType } = props
    this.state = {
      paymentMethod: paymentMethod || '',
      paymentType: paymentType || 'null',
      recipient: ''
    }
  }

  renderSpinner = (height) => {
    return <Spinner name='circle' color='white' fadeIn='none' style={{ marginLeft: 'auto', marginRight: 'auto', height }} />
  }

  onPaymentTypeChange = (event) => {
    const { clearPaymentFormFeedback } = this.props
    clearPaymentFormFeedback()
    this.setState({
      paymentType: event.target.value
    })
  }

  onPaymentMethodChange = (event) => {
    const { fetchMinerPayoutScript, fetchMinerPaymentTxSlate, clearPaymentFormFeedback } = this.props
    clearPaymentFormFeedback()
    const paymentMethod = event.target.value
    this.setState({
      paymentMethod
    })
    if (paymentMethod === 'payoutScript') {
      fetchMinerPayoutScript()
    } else if (paymentMethod === 'txSlate') {
      fetchMinerPaymentTxSlate()
    }
  }

  onChangeTextInput = (event) => {
    this.setState({
      recipient: event.target.value
    })
  }

  _downloadTxtFile = () => {
    const { minerPaymentTxSlate } = this.props
    const element = document.createElement('a')
    const file = new Blob([minerPaymentTxSlate], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    const date = new Date()
    const timestamp = Math.floor(date.getTime() / 1000)
    element.download = `txSlate-${timestamp}.txt`
    element.click()
  }

  _downloadPayoutScriptFile = () => {
    const { payoutScript } = this.props
    const element = document.createElement('a')
    const file = new Blob([payoutScript], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    const date = new Date()
    const timestamp = Math.floor(date.getTime() / 1000)
    element.download = `payoutScript-${timestamp}.txt`
    element.click()
  }

  componentDidMount = () => {
    const { getLatestMinerPayments } = this.props
    getLatestMinerPayments()
  }

  renderManualPayoutOptions = () => {
    return (
      <div style={{ marginBottom: '20px' }}>
        <legend className='col-form-label' style={{ marginBottom: '10px' }}>Payment Method:</legend>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onPaymentMethodChange} type='radio' value='http' name='paymentMethod' />Online Wallet / Port
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onPaymentMethodChange} type='radio' value='keybase' name='paymentMethod' />Keybase Username
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onPaymentMethodChange} type='radio' value='payoutScript' name='paymentMethod' />Download Payout Script
          </Label>
        </FormGroup>
      </div>
    )
  }

  renderAutomaticPayoutOptions = () => {
    return (
      <div style={{ marginBottom: '20px' }}>
        <legend className='col-form-label' style={{ marginBottom: '10px' }}>Payment Method:</legend>
        <FormGroup>
          <p>Scheduled payouts occur multiple times per day, although exact payout schedules may vary.</p><br />
          <div style={{ textAlign: 'center' }}>
            <Alert color='warning' style={{ width: '80%', textAlign: 'center', display: 'inline-block' }}>Please be aware that automated payouts require a <strong>5 GRIN</strong> minimum balance in order to be triggered.</Alert>
          </div>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onPaymentMethodChange} type='radio' value='http' name='paymentMethod' />Online Wallet / Port
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onPaymentMethodChange} type='radio' value='keybase' name='paymentMethod' />Keybase Username
          </Label>
        </FormGroup>
      </div>
    )
  }

  renderOptions = () => {
    const { paymentType } = this.state
    switch (paymentType) {
      case 'manual':
        return this.renderManualPayoutOptions()
      case 'scheduled':
        return this.renderAutomaticPayoutOptions()
      case 'null':
        return null
      default:
        return null
    }
  }

  renderPayoutForm = () => {
    const { isTxSlateLoading } = this.props
    const { paymentMethod, paymentType } = this.state
    if (paymentType !== 'none') {
      switch (paymentMethod) {
        case 'http':
          return (
            <div>
              <Label for="onlineWallet">Enter Wallet &amp; Port:</Label>
              <Input
                onChange={this.onChangeTextInput}
                type="text"
                name="onlineWallet"
                id="onlineWallet"
                placeholder="195.128.200.15:13415"
                className='form-control' />
            </div>
          )
        case 'keybase':
          return (
            <div>
              <Label for="onlineWallet">Enter Keybase Username:</Label>
              <Input
                onChange={this.onChangeTextInput}
                type="text"
                name="keybase"
                id="keybase"
                placeholder="myKeybaseUser"
                className='form-control' />
            </div>
          )
        case 'payoutScript':
          return (
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <Label for="payoutScript">Download the Payout Script:</Label><br />
              <a href='' onClick={this._downloadPayoutScriptFile} style={{ fontWeight: 'bold' }}>Download</a>
            </div>
          )
        case 'txSlate':
          return (
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <Label for="txSlate">Download the Transaction Slate and Upload to Wallet:</Label><br />
              {isTxSlateLoading ? (
                this.renderSpinner('1.8em')
              ) : (
                <a href='' onClick={this._downloadTxtFile} style={{ fontWeight: 'bold' }}>Download</a>
              )}
            </div>
          )
      }
    } else {
      return null
    }
  }

  onSubmit = (e) => {
    e.preventDefault()
    const { setPaymentMethodSetting } = this.props
    setPaymentMethodSetting(this.state)
  }

  render () {
    const { paymentType, paymentMethod } = this.state
    const { isPaymentSettingProcessing, paymentFormFeedback } = this.props

    const isFormShown = paymentType !== 'manual' || (paymentType === 'manual' && (paymentMethod === 'http' || paymentMethod === 'keybase'))
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
                    <Input defaultValue={paymentType} type='select' name='paymentType' id='paymentSelect' onChange={this.onPaymentTypeChange}>
                      <option value='null'>------------</option>
                      <option value='scheduled'>Scheduled Payout</option>
                      <option value='manual'>Manual Payout</option>
                    </Input>
                  </FormGroup>
                  {this.renderOptions()}
                  {this.renderPayoutForm()}
                  {isFormShown && (
                    <div style={{ marginTop: '30px' }}>
                      <div style={{ textAlign: 'center' }}>
                        {/* <button className="btn btn-outline-primary account__btn account__btn--small" onClick={this.onClear}>{'Clear'}</button> */ }ß
                        <button className="btn btn-primary account__btn account__btn--small" style={{ width: '104px' }} onClick={this.onSubmit} disabled={isPaymentSettingProcessing}>
                          {isPaymentSettingProcessing ? this.renderSpinner('21px') : 'Submit'}
                        </button>
                      </div>
                      <div style={{ textAlign: 'center', marginTop: '10px' }}>
                        {paymentFormFeedback && <Alert style={{ display: 'inline' }} color={paymentFormFeedback.color}>{paymentFormFeedback.message}</Alert> }
                      </div>
                    </div>
                  )}
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
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody>
                <LatestMinerPaymentsConnector />
              </CardBody>
            </Card>
          </Col>
        </Row>
      </Container>
    )
  }
}
