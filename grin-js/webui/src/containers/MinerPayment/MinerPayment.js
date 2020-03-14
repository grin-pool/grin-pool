import React, { Component } from 'react'
import { Col, Container, Row, Card, CardBody, Form, FormGroup, Label, Input, Alert } from 'reactstrap'
import { MinerPaymentDataConnector } from '../../redux/connectors/MinerPaymentDataConnector.js'
import { LatestMinerPaymentsConnector } from '../../redux/connectors/LatestMinerPaymentsConnector.js'
import Blob from 'blob'
import Spinner from 'react-spinkit'
import ReactGA from 'react-ga'
import { API_URL_V2 } from '../../config.js'
import { C31_COLOR } from '../../custom/custom.js'

export class MinerPaymentComponent extends Component {
  constructor (props) {
    super(props)
    const { paymentMethod, paymentType } = props
    this.state = {
      paymentMethod: paymentMethod || '',
      paymentType: paymentType || 'null',
      recipient: ''
    }
    ReactGA.initialize('UA-132063819-1')
    ReactGA.pageview(window.location.pathname + window.location.search)
  }

  renderSpinner = (height) => {
    return <Spinner name='circle' color='white' fadeIn='none' style={{ marginLeft: 'auto', marginRight: 'auto', height }} />
  }

  onPaymentTypeChange = (event) => {
    const { clearPaymentFormFeedback } = this.props
    let paymentType = event.target.value
    let { paymentMethod, recipient } = this.state
    clearPaymentFormFeedback()

    if (paymentType === 'hotbit') {
      paymentType = 'manual'
      paymentMethod = 'http'
      recipient = 'https://grin.hotbit.io:443/'
    } else if (paymentType === 'bitmesh') {
      paymentType = 'manual'
      paymentMethod = 'http'
      recipient = 'someRandomCharacters.g.bitmesh.com:80'
    } else if (paymentType === 'kucoin') {
      paymentType = 'manual'
      paymentMethod = 'http'
      recipient = 'https://depositgrin.kucoin.com:443/deposit/'
    }
    this.setState({
      paymentType,
      paymentMethod,
      recipient
    })
  }

  onPaymentMethodChange = (event) => {
    const { fetchMinerPaymentTxSlate, clearPaymentFormFeedback } = this.props
    clearPaymentFormFeedback()
    const paymentMethod = event.target.value
    this.setState({
      paymentMethod
    })
    if (paymentMethod === 'txSlate') {
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

  componentDidMount = () => {
    const { getLatestMinerPayments } = this.props
    getLatestMinerPayments()
  }

  renderManualPayoutOptions = () => {
    const { paymentMethod } = this.state
    return (
      <div style={{ marginBottom: '20px' }}>
        <legend className='col-form-label' style={{ marginBottom: '10px' }}>Payment Method:</legend>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onPaymentMethodChange} type='radio' value='http' name='paymentMethod' checked={paymentMethod === 'http'} />Online Wallet / Port
          </Label>
        </FormGroup>
        <FormGroup check>
          <Label check>
            <Input onChange={this.onPaymentMethodChange} type='radio' value='payoutScript' name='paymentMethod' checked={paymentMethod === 'payoutScript'} />Download Payout Script
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
      case 'hotbit':
        return this.renderManualPayoutOptions()
      case 'bitmesh':
        return this.renderManualPayoutOptions()
      case 'kucoin':
        return this.renderManualPayoutOptions()
      case 'null':
        return null
      default:
        return null
    }
  }

  renderPayoutForm = () => {
    const { isTxSlateLoading } = this.props
    const { paymentMethod, paymentType, recipient } = this.state
    if (paymentType !== 'none') {
      switch (paymentMethod) {
        case 'http':
          return (
            <div>
              <Label for="onlineWallet">Enter Wallet &amp; Port:</Label>
              <Alert color='danger' style={{ textAlign: 'center', position: 'relative', marginTop: '16px', marginBottom: '26px' }}><strong>We do NOT recommend sending directly to an exchange, and you do so at your own risk! If you send to an exchange please consider including the port number.</strong></Alert>
              <Input
                onChange={this.onChangeTextInput}
                type="text"
                name="onlineWallet"
                id="onlineWallet"
                placeholder="195.128.200.15:3415"
                className='form-control'
                value={recipient}
              />
            </div>
          )
        case 'payoutScript':
          return (
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <Label for="payoutScript">Download the Payout Script:</Label><br />
              <a href={`${API_URL_V2}public/GP_payout.py`} style={{ fontWeight: 'bold' }} download>Download</a>
              <p>Click here on instruction on how to use the <a style={{ fontWeight: 'bold' }} href='https://youtu.be/EVRWarvaq8Q' rel='noopener noreferrer' target='_blank'>payment script</a> and <a href='https://youtu.be/EVRWarvaq8Q?t=1096' rel='noopener noreferrer' style={{ fontWeight: 'bold' }} target='_blank'>create a tx slate for upload</a></p>
            </div>
          )
        case 'txSlate':
          return (
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <Label for="txSlate">Download the Transaction Slate and Upload to Wallet:</Label><br />
              {isTxSlateLoading ? (
                this.renderSpinner('1.8em')
              ) : (
                <a href='#' onClick={this._downloadTxtFile} style={{ fontWeight: 'bold' }}>Download</a>
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
    const { setPaymentMethodSetting, rejectZeroBalancePayment, dueAmount, rejectEmptyRecipient } = this.props
    if (this.state.recipient.trim() === '') {
      rejectEmptyRecipient()
      return
    } else if (dueAmount <= 0) {
      rejectZeroBalancePayment()
      return
    }
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
                <Alert color='danger' style={{ textAlign: 'center', position: 'relative', marginTop: '16px' }}>Please be aware that current GRIN payment methods are still under development. We ask for your patience as we test and implement additional payment options.</Alert>
                <br />
                <h4>Examples</h4>
                <ul>
                  <li><strong>BitMesh</strong>: <span style={{ color: C31_COLOR }}>fysomethingjxd7e6.g.bitmesh.com:80</span> <span style={{ display: 'block', float: 'right' }}>(Manual Payout -> Online Wallet / Port)</span></li>
                  <li><strong>HotBit</strong>:  <span style={{ color: C31_COLOR }}>https://grin.hotbit.io<strong>:443</strong>/555555</span> <span style={{ display: 'block', float: 'right' }}>(Manual Payout -> Online Wallet / Port)</span></li>
                  <li><strong>TradeOgre</strong>: follow <a href='https://youtu.be/EVRWarvaq8Q' target='_blank' rel='noopener noreferrer' style={{ color: C31_COLOR }}>instructions</a> <span style={{ display: 'block', float: 'right' }}>(Manual Payout -> Download Payout Script)</span></li>
                </ul>
                <br />
                <Form className='minerPaymentForm'>
                  <FormGroup>
                    <Label for='paymentType'>Payment Type:</Label>
                    <Input defaultValue={paymentType} type='select' name='paymentType' id='paymentSelect' onChange={this.onPaymentTypeChange}>
                      <option value='null'>------------</option>
                      <option value='manual'>Manual Payout</option>
                      <option value='hotbit'>HotBit</option>
                      <option value='bitmesh'>BitMesh</option>
                      <option value='kucoin'>Kucoin</option>
                    </Input>
                  </FormGroup>
                  {this.renderOptions()}
                  {this.renderPayoutForm()}
                  {isFormShown && (
                    <div style={{ marginTop: '30px' }}>
                      <div style={{ textAlign: 'center' }}>
                        {/* <button className="btn btn-outline-primary account__btn account__btn--small" onClick={this.onClear}>{'Clear'}</button> */ }
                        <button className="btn btn-primary account__btn account__btn--small" style={{ width: '104px' }} onClick={this.onSubmit} disabled={isPaymentSettingProcessing || this.state.paymentType === 'null'}>
                          {isPaymentSettingProcessing ? this.renderSpinner('21px') : 'Submit'}
                        </button>
                      </div>
                      <div style={{ textAlign: 'center', marginTop: '10px' }}>
                        {paymentFormFeedback && <Alert style={{ display: 'block' }} color={paymentFormFeedback.color}>{paymentFormFeedback.message}</Alert> }
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
