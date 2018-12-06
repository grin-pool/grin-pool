import React, { Component } from 'react'
import { Table } from 'reactstrap'
import { secondsToHms } from '../../utils/utils.js'

export class MinerPaymentDataComponent extends Component {
  interval = null

  componentWillUnmount = () => {
    clearInterval(this.interval)
  }

  UNSAFE_componentWillMount () {
    this.fetchMinerPaymentData()
    this.interval = setInterval(this.fetchMinerPaymentData, 30000)
  }

  fetchMinerPaymentData = () => {
    const { fetchMinerPaymentData } = this.props
    fetchMinerPaymentData()
  }

  render () {
    const { amount, address, lastSuccess, failureCount, lastTry, currentTimestamp } = this.props
    const lastTryTimeAgo = secondsToHms(currentTimestamp - lastTry)

    return (
      <div>
        <h4>Payment Info</h4>
        <Table size='sm'>
          <tbody>
            <tr>
              <td>Amount Due</td>
              <td>{amount} GRIN</td>
            </tr>
            <tr>
              <td>Payout Address</td>
              <td>{address || 'n/a'}</td>
            </tr>
            <tr>
              <td>Last Payout</td>
              <td>{lastSuccess || 'n/a'}</td>
            </tr>
            <tr>
              <td>Payout Attempt Failures</td>
              <td>{failureCount}</td>
            </tr>
            <tr>
              <td>Last Auto Payout Attempt</td>
              <td>{lastTryTimeAgo}</td>
            </tr>
          </tbody>
        </Table>
      </div>
    )
  }
}
