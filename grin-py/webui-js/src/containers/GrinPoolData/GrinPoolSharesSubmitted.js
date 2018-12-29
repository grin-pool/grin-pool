import React, { Component } from 'react'
import { Row, Col, Table } from 'reactstrap'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { C29_COLOR } from '../../custom/custom.js'

export class GrinPoolSharesSubmittedComponent extends Component {
  UNSAFE_componentWillMount () {
    const { fetchGrinPoolSharesSubmitted } = this.props
    fetchGrinPoolSharesSubmitted()
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight, fetchGrinPoolSharesSubmitted } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      fetchGrinPoolSharesSubmitted()
    }
  }

  render () {
    const { sharesSubmitted } = this.props
    const length = sharesSubmitted.length
    let totalSharesSubmitted = 0
    if (sharesSubmitted[length - 1]) {
      totalSharesSubmitted = sharesSubmitted[length - 1].total_shares_processed
    }

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Pool Shares Submitted</h4>
          <Table size='sm'>
            <tbody>
              <tr>
                <td>Total Shares Submitted</td>
                <td>{totalSharesSubmitted}</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={12} lg={7} xl={9}>
          <ResponsiveContainer width='100%' height={270}>
            <LineChart isAnimationActive={false} data={sharesSubmitted} >
              <XAxis interval={19} dataKey='height'/>
              <Tooltip />
              <Legend verticalAlign='top' height={36}/>
              <YAxis connectNulls={true} yAxisId='left' orientation='left' stroke={C29_COLOR} allowDecimals={true} />
              <Line dot={false} yAxisId='left' name='Pool Shares Submitted' dataKey='shares_processed' stroke={C29_COLOR} />
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
    )
  }
}
