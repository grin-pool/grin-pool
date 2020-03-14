import React, { Component } from 'react'
import { Row, Col, Table } from 'reactstrap'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { C31_COLOR } from '../../custom/custom.js'

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

    const filteredSharesSubmitted = sharesSubmitted.filter((block) => block.height % 5 === 0)
    let cumulativeWorkerCount = 0
    let maxWorkers = 0
    filteredSharesSubmitted.forEach(block => {
      cumulativeWorkerCount = cumulativeWorkerCount + block.active_miners
      if (block.active_miners > maxWorkers) maxWorkers = block.active_miners
    })
    const averageWorkerCount = (cumulativeWorkerCount / filteredSharesSubmitted.length).toFixed(1)
    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Pool Active Workers</h4>
          <Table size='sm'>
            <tbody>
              <tr>
                <td>1440-block Average Active Workers</td>
                <td>{averageWorkerCount}</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={12} lg={7} xl={9}>
          <ResponsiveContainer width='100%' height={270}>
            <LineChart isAnimationActive={false} data={filteredSharesSubmitted} >
              <XAxis interval={19} dataKey='height'/>
              <Tooltip />
              <Legend verticalAlign='top' height={36}/>
              <YAxis connectNulls={true} yAxisId='left' orientation='left' stroke={C31_COLOR} domain={[0, Math.ceil(maxWorkers * 1.3)]} />
              <Line dot={false} yAxisId='left' name='Pool Active Workers' dataKey='active_miners' stroke={C31_COLOR} />
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
    )
  }
}
