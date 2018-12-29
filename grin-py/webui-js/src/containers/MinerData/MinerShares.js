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
    const { fetchMinerData, fetchMinerShares } = this.props
    fetchMinerData()
    fetchMinerShares()
  }

  render () {
    const { minerData, totalSharesSubmitted } = this.props

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Miner Valid Shares Submitted</h4>
          <Table size='sm'>
            <tbody>
              <tr>
                <td>Total Valid Shares Submitted</td>
                <td>{totalSharesSubmitted}</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={12} lg={7} xl={9}>
          <ResponsiveContainer width='100%' height={270}>
            <LineChart isAnimationActive={false} data={minerData} >
              <XAxis interval={19} dataKey='height'/>
              <Tooltip />
              <Legend verticalAlign='top' height={36}/>
              <YAxis connectNulls={false} yAxisId='left' orientation='left' stroke={C29_COLOR} allowDecimals={false} />
              <Line dot={false} yAxisId='left' name='Miner Valid Shares Submitted' dataKey='valid_shares' stroke={C29_COLOR} />
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
    )
  }
}
