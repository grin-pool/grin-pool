import React, { Component } from 'react'
import { Col, Row, Table } from 'reactstrap'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { C29_COLOR } from '../../custom/custom.js'

export class MinerSharesComponent extends Component {
  UNSAFE_componentWillMount () {
    this.fetchMinerData()
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      this.fetchMinerData()
    }
  }

  fetchMinerData = () => {
    const { fetchMinerData, fetchMinerTotalValidShares } = this.props
    fetchMinerData()
    fetchMinerTotalValidShares()
  }

  render () {
    const { minerData, totalSharesSubmitted } = this.props
    let validShareCount = 0
    let invalidShareCount = 0
    let staleShareCount = 0

    let blockCount = 0
    let periodValidShareCount = 0
    let periodInvalidShareCount = 0
    let periodStaleShareCount = 0
    const periodData = []
    minerData.forEach(block => {
      blockCount++
      validShareCount += block.valid_shares
      invalidShareCount += block.invalid_shares
      staleShareCount += block.stale_shares

      periodValidShareCount += block.valid_shares
      periodInvalidShareCount += block.invalid_shares
      periodStaleShareCount += block.stale_shares
      if (blockCount % 5 === 0) {
        periodData.push({
          height: block.height,
          periodValidShareCount,
          periodInvalidShareCount,
          periodStaleShareCount,
          timestamp: block.timestamp
        })
        periodValidShareCount = 0
        periodInvalidShareCount = 0
        periodStaleShareCount = 0
      }
    })

    const totalShareCount = validShareCount + invalidShareCount + staleShareCount
    const validShareRate = ((validShareCount / totalShareCount) * 100).toFixed(2)
    const invalidShareRate = ((invalidShareCount / totalShareCount) * 100).toFixed(2)
    const staleShareRate = ((staleShareCount / totalShareCount) * 100).toFixed(2)

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Miner Valid Shares Submitted</h4>
          <Table size='sm'>
            <tbody>
              <tr>
                <td>1440-block Valid Shares</td>
                <td>{validShareCount} ({validShareRate}%)</td>
              </tr>
              <tr>
                <td>1440-block Rejected Shares</td>
                <td>{invalidShareCount} ({invalidShareRate}%)</td>
              </tr>
              <tr>
                <td>1440-block Stale Shares</td>
                <td>{staleShareCount} ({staleShareRate}%)</td>
              </tr>
              <tr>
                <td>Total Valid Shares Submitted</td>
                <td>{totalSharesSubmitted}</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={12} lg={7} xl={9}>
          <ResponsiveContainer width='100%' height={270}>
            <LineChart isAnimationActive={false} data={periodData} >
              <XAxis tickCount={7} dataKey='timestamp' tickFormatter={(value) => new Date(value * 1000).toLocaleTimeString()} type={'number'} domain={['dataMin', new Date().getTime() / 1000]} />
              <Legend verticalAlign='top' height={36}/>
              <YAxis connectNulls={false} yAxisId='left' orientation='left' stroke={C29_COLOR} allowDecimals={false} />
              <Line dot={false} yAxisId='left' name='Valid' dataKey='periodValidShareCount' stroke={C29_COLOR} />
              <Line dot={false} yAxisId='left' name='Rejected' dataKey='periodInvalidShareCount' stroke={'red'} />
              <Line dot={false} yAxisId='left' name='Stale' dataKey='periodStaleShareCount' stroke={'orange'} />
              <Tooltip content={<WorkerShareDataCustomTooltip />} />
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
    )
  }
}

export class WorkerShareDataCustomTooltip extends Component {
  render () {
    const { active } = this.props

    if (active) {
      const { payload } = this.props
      if (!payload) return null
      return (
        <div className='custom-network-data-tooltip'>
          <p>Block: {payload[0].payload.height}</p>
          <p>Timestamp: {new Date(payload[0].payload.timestamp * 1000).toLocaleTimeString()}</p>
          <p>Valid Shares: {payload[0].payload.periodValidShareCount}</p>
          <p>Invalid Shares: {payload[0].payload.periodInvalidShareCount}</p>
          <p>Stale Shares: {payload[0].payload.periodStaleShareCount}</p>
        </div>
      )
    }

    return null
  }
}
