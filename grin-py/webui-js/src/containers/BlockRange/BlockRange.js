import React, { Component } from 'react'
import { Input, Row, Table } from 'reactstrap'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'
import { secondsToHms } from '../../utils/utils.js'

export class BlockRange extends Component {
  constructor (props) {
    super(props)
    this.state = {
      range: 20
    }
  }
  componentDidMount () {
    const { fetchBlockRange } = this.props
    const { range } = this.state
    fetchBlockRange(null, range)
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight, fetchBlockRange } = this.props
    const { range } = this.state
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      fetchBlockRange(null, range)
    }
  }

  changeRangeSize = (e) => {
    const { fetchBlockRange } = this.props
    const newRange = parseInt(e.target.value)
    fetchBlockRange(null, newRange)
    this.setState({
      range: newRange
    })
  }

  render () {
    const { recentBlocks, graphTitle } = this.props
    const { range } = this.state

    const rows = []
    if (recentBlocks.length) {
      for (let i = 1; i <= range && i <= recentBlocks.length - 1; i++) {
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
        <div style={{ width: '100%', marginBottom: '14px' }}>
          <h4 className='page-title' style={{ marginBottom: 36, display: 'inline' }}>{graphTitle}</h4>
          <Input type="select" name="select" onChange={this.changeRangeSize} style={{ display: 'inline', float: 'right', width: '100px' }}>
            <option>20</option>
            <option>100</option>
            <option>500</option>
          </Input>
        </div>

        <Table size='sm' responsive hover>
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
