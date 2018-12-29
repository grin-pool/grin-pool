import React, { Component } from 'react'
import { Row, Table } from 'reactstrap'
import { C29_COLOR } from '../../custom/custom.js'
import { secondsToHms } from '../../utils/utils.js'
export class GrinPoolRecentBlocks extends Component {
  componentDidMount () {
    const { fetchGrinPoolRecentBlocks } = this.props
    fetchGrinPoolRecentBlocks()
  }

  render () {
    const { recentBlocks } = this.props

    const rows = []
    if (recentBlocks.length) {
      for (let i = 1; i <= 20 && i <= recentBlocks.length - 1; i++) {
        const block = recentBlocks[recentBlocks.length - i]
        const currentTimestamp = new Date().getTime()
        const paymentSecondsAgo = currentTimestamp / 1000 - block.timestamp
        const readableTimeAgo = secondsToHms(paymentSecondsAgo)
        rows.push(
          <tr key={block.height}>
            <td><a style={{ color: C29_COLOR }} href={`https://grinscan.net/block/${block.height}`}>{block.height}</a></td>
            <td>{block.nonce}</td>
            <td>{block.hash}</td>
            <td>{readableTimeAgo} ago</td>
            <td>{block.state}</td>
            <td style={{ textAlign: 'right' }}>{block.actual_difficulty}</td>
          </tr>
        )
      }
    }

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <h4 className='page-title' style={{ marginBottom: 36 }}>Recent Blocks Found by Pool</h4>
        <Table size='sm' responsive hover className='grinPoolStatsTable'>
          <thead>
            <tr>
              <th>Height</th>
              <th>Nonce</th>
              <th>Hash</th>
              <th>Time</th>
              <th>State</th>
              <th style={{ textAlign: 'right' }}>Difficulty</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </Table>
      </Row>
    )
  }
}
