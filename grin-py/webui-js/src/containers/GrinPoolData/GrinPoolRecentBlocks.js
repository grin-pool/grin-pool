import React, { Component } from 'react'
import { Row, Table } from 'reactstrap'

export class GrinPoolRecentBlocks extends Component {
  componentDidMount () {
    const { fetchGrinPoolRecentBlocks } = this.props
    fetchGrinPoolRecentBlocks()
  }

  render () {
    const { recentBlocks } = this.props

    const rows = []
    if (recentBlocks.length) {
      for (let i = 1; i <= 30; i++) {
        const block = recentBlocks[recentBlocks.length - i]
        rows.push(
          <tr key={block.height}>
            <td><a href={`https://grinscan.net/block/${block.height}`}>{block.height}</a></td>
            <td>{block.nonce}</td>
            <td>{block.hash}</td>
            <td>{block.timestamp}</td>
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
              <th>Timestamp</th>
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
