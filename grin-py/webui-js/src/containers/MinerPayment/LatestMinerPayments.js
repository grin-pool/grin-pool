import React, { Component } from 'react'
import { Row, Table } from 'reactstrap'
import { nanoGrinToGrin, secondsToHms } from '../../utils/utils.js'

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
        const currentTimestamp = new Date().getTime()
        const paymentSecondsAgo = currentTimestamp / 1000 - payment.timestamp
        const readableTimeAgo = secondsToHms(paymentSecondsAgo)
        return (
          <tr key={payment.id}>
            <td>{payment.id}</td>
            <td>{payment.address}</td>
            <td>{nanoGrinToGrin(payment.amount)} GRIN</td>
            <td>{nanoGrinToGrin(payment.fee)} GRIN</td>
            <td>{payment.state}</td>
            <td>{payment.height}</td>
            <td style={{ textAlign: 'right' }}>{readableTimeAgo} ago</td>
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
