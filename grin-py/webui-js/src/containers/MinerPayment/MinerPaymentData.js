import React, { Component } from 'react'
import { Table, Alert } from 'reactstrap'
import { secondsToHms, nanoGrinToGrin } from '../../utils/utils.js'

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
    const readableAmount = amount > 0 ? amount : 0
    const lastTryTimeAgo = secondsToHms(currentTimestamp - lastTry)
    const lastPayoutTimeAgo = lastSuccess ? secondsToHms(currentTimestamp - lastSuccess) : 'n/a'
    return (
      <div>
        <h4>Payment Info</h4>
        <div style={{ marginTop: '18px', marginBottom: '18px', textAlign: 'center' }}>
          <Alert color='light' style={{ textAlign: 'center', width: '80%', display: 'inline-block' }}>Please be aware that work takes ~24 hours to be credited, as the blocks acquire sufficient confirmations.</Alert>
        </div>
        <Table size='sm'>
          <tbody>
            <tr>
              <td>Amount Due</td>
              <td>{nanoGrinToGrin(readableAmount)} GRIN</td>
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
