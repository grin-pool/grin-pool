import React, { Component } from 'react'
import { Table } from 'reactstrap'
import { secondsToHms } from '../../utils/utils.js'

export class MinerPaymentDataComponent extends Component {
  UNSAFE_componentWillMount () {
    this.fetchMinerPaymentData()
  }

  componentDidUpdate (prevProps) {
    const { lastestBlockHeight } = this.props
    if (prevProps.lastestBlockHeight !== lastestBlockHeight) {
      this.fetchMinerPaymentData()
    }
  }

  fetchMinerPaymentData = () => {
    const { fetchMinerPaymentData } = this.props
    fetchMinerPaymentData()
  }

  render () {
    const { amount, address, lastSuccess, failureCount, lastTry, currentTimestamp } = this.props
    const lastTryTimeAgo = secondsToHms(currentTimestamp - lastTry)
    const lastPayoutTimeAgo = secondsToHms(currentTimestamp - lastSuccess)
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
              <td>{lastPayoutTimeAgo || 'n/a'}</td>
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
