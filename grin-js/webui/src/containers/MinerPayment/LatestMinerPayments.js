import React, { Component } from 'react'
import { Row, Table } from 'reactstrap'
import { nanoGrinToGrin } from '../../utils/utils.js'
import { CANCELED_PAYMENT_COLOR, EXPIRED_PAYMENT_COLOR } from '../../custom/custom.js'

export class LatestMinerPayments extends Component {
  componentDidMount () {
    this.getLatestMinerPaymentRange()
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      this.getLatestMinerPaymentRange()
    }
  }

  getLatestMinerPaymentRange = () => {
    const { getLatestMinerPaymentRange } = this.props
    getLatestMinerPaymentRange()
  }

  render () {
    const { latestMinerPayments } = this.props
    let paymentRows = []
    if (latestMinerPayments.length) {
      latestMinerPayments.sort((a, b) => b.timestamp - a.timestamp)
      paymentRows = latestMinerPayments.map(payment => {
        let line = null
        let color = null
        if (payment.state === 'expired') {
          line = 'line-through'
          color = EXPIRED_PAYMENT_COLOR
        } else if (payment.state === 'canceled') {
          line = 'line-through'
          color = CANCELED_PAYMENT_COLOR
        }
        const textDecoration = {
          textDecorationLine: line,
          textDecorationColor: color
        }
        let txId = ''
        try {
          const txData = JSON.parse(payment.tx_data)
          txId = txData ? txData.id : ''
        } catch (e) {
          console.log('Could not parse')
        }

        return (
          <tr key={payment.id}>
            <td style={textDecoration}>{payment.id}</td>
            <td style={textDecoration}>{txId}</td>
            <td style={textDecoration}>{payment.address}</td>
            <td style={textDecoration}>{nanoGrinToGrin(payment.amount)} GRIN</td>
            <td style={textDecoration}>{nanoGrinToGrin(payment.fee)} GRIN</td>
            <td style={textDecoration}>{payment.state}</td>
            <td style={textDecoration}>{payment.height}</td>
            <td style={{ textAlign: 'right', ...textDecoration }}>{new Date(payment.timestamp).toLocaleString()}</td>
          </tr>
        )
      })
    }

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <h4 className='page-title' style={{ marginBottom: 36 }}>Recent Payouts</h4>
        <Table responsive hover>
          <thead>
            <tr>
              <th>ID</th>
              <th>Transaction ID</th>
              <th>Address</th>
              <th>Amount</th>
              <th>Fee</th>
              <th>State</th>
              <th>Block Height</th>
              <th style={{ textAlign: 'right' }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {paymentRows}
          </tbody>
        </Table>
      </Row>
    )
  }
}
