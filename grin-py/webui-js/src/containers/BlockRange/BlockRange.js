import React, { Component } from 'react'
import { Row, Table } from 'reactstrap'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'
import { secondsToHms } from '../../utils/utils.js'

export class BlockRange extends Component {
  componentDidMount () {
    const { fetchBlockRange } = this.props
    fetchBlockRange()
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight, fetchBlockRange } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      fetchBlockRange()
    }
  }

  render () {
    const { recentBlocks, graphTitle } = this.props

    const rows = []
    if (recentBlocks.length) {
      for (let i = 1; i <= 20 && i <= recentBlocks.length - 1; i++) {
        const block = recentBlocks[recentBlocks.length - i]
        const currentTimestamp = new Date().getTime()
        const paymentSecondsAgo = currentTimestamp / 1000 - block.timestamp
        const readableTimeAgo = secondsToHms(paymentSecondsAgo)
        const colors = {
          C29: C29_COLOR,
          C31: C31_COLOR
        }
        const rowColor = colors[`C${block.edge_bits}`]
        rows.push(
          <tr key={block.height}>
            <td><a style={{ color: rowColor || C29_COLOR }} href={`https://floonet.grinexplorer.net/block/${block.height}`} rel='noopener noreferrer' target='_blank' >{block.height}</a></td>
            <td>{block.nonce}</td>
            <td>{block.hash}</td>
            {block.edge_bits && <td style={{ color: rowColor }}>C{block.edge_bits}</td>}
            <td>{readableTimeAgo} ago</td>
            <td>{block.state}</td>
            <td style={{ textAlign: 'right' }}>{block.actual_difficulty || block.total_difficulty}</td>
          </tr>
        )
      }
    }

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <h4 className='page-title' style={{ marginBottom: 36 }}>{graphTitle}
        </h4>
        <Table size='sm' responsive hover className='grinPoolStatsTable'>
          <thead>
            <tr>
              <th>Height</th>
              <th>Nonce</th>
              <th>Hash</th>
              {recentBlocks[0] && recentBlocks[0].edge_bits && <th>Algo</th>}
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
