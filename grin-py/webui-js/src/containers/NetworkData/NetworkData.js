import React, { Component } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Row, Col, Table } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const C29_COLOR = '#8884d8'
const C30_COLOR = '#cc9438'

export class NetworkDataComponent extends Component {
  interval = null

  componentWillUnmount = () => {
    clearInterval(this.interval)
  }

  UNSAFE_componentWillMount () {
    const { fetchNetworkData } = this.props
    fetchNetworkData()
    this.interval = setInterval(fetchNetworkData, 10000)
  }

  render () {
    const { networkData, latestBlock } = this.props
    const graphRateData = []
    let maxC29Gps = 0
    let minC29Gps = 0
    let maxC30Gps = 0
    let minC30Gps = 0

    networkData.forEach((block) => {
      if (block.gps[0]) {
        if (block.gps[0].gps > maxC29Gps || !maxC29Gps) maxC29Gps = block.gps[0].gps
        if (block.gps[0].gps < minC29Gps || !minC29Gps) minC29Gps = block.gps[0].gps
      }
      if (block.gps[1]) {
        if (block.gps[1].gps > maxC30Gps || !maxC30Gps) maxC30Gps = block.gps[1].gps
        if (block.gps[1].gps < minC30Gps || !minC30Gps) minC30Gps = block.gps[1].gps
      }

      graphRateData.push({
        height: block.height,
        gps: block.gps,
        difficulty: block.difficulty
      })
    })
    let c29LatestGraphRate = 'C29 = 0 gps'
    let c30LatestGraphRate = 'C30 = 0 gps'
    let latestDifficulty = 'n/a'
    let latestBlockHeight = 'n/a'
    if (networkData.length > 0) {
      const lastBlock = networkData[networkData.length - 1]
      if (lastBlock.gps[0]) {
        c29LatestGraphRate = `C${lastBlock.gps[0].edge_bits} = ${lastBlock.gps[0].gps.toFixed(2)} gps`
      }
      if (lastBlock.gps[1]) {
        c30LatestGraphRate = `C${lastBlock.gps[1].edge_bits} = ${lastBlock.gps[1].gps.toFixed(2)} gps`
      }
      latestDifficulty = lastBlock.difficulty
      latestBlockHeight = lastBlock.height
    } else {
      c29LatestGraphRate = '0 gps'
      c30LatestGraphRate = '0 gps'
      latestDifficulty = 'n/a'
      latestBlockHeight = 'n/a'
    }
    const nowTimestamp = Date.now()
    const latestBlockTimeAgo = latestBlock.timestamp ? Math.floor((nowTimestamp / 1000) - latestBlock.timestamp) : ''
    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Network Stats</h4>
          <Table>
            <tbody>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'chart-line'} /> Graph Rate</td>
                <td><span style={{ color: C29_COLOR }}>{c29LatestGraphRate}</span><br /><span style={{ color: C30_COLOR }}>{c30LatestGraphRate}</span></td>
              </tr>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'clock'} /> Block Found</td>
                <td>{latestBlockTimeAgo} sec ago</td>
              </tr>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'desktop'} />Difficulty</td>
                <td>{latestDifficulty}</td>
              </tr>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'link'} />Chain Height</td>
                <td>{latestBlockHeight}</td>
              </tr>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'dollar-sign'} />Reward</td>
                <td>60 GRIN / block</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={12} lg={7} xl={9}>
          <ResponsiveContainer width='100%' height={270}>
            <LineChart isAnimationActive={false} data={graphRateData} >
              <XAxis interval={19} dataKey='height'/>
              <Tooltip />
              <Legend verticalAlign='top' height={36}/>
              <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} connectNulls={true} yAxisId='left' orientation='left' stroke={C29_COLOR} domain={[minC29Gps, maxC29Gps]} allowDecimals={true} />
              <Line dot={false} yAxisId='left' name='C29 (GPU) Graph Rate' dataKey='gps[0].gps' stroke={C29_COLOR} />
              <YAxis connectNulls={true} yAxisId='right' orientation='right' stroke={C30_COLOR} domain={[minC30Gps, maxC30Gps]} allowDecimals={true} />
              <Line dot={false} yAxisId='right' name='C30 (ASIC) Graph Rate' dataKey='gps[1].gps' stroke={C30_COLOR} />
              {/* <YAxis yAxisId='right' orientation='right' domain={[minDifficulty, maxDifficulty]} stroke='#82ca9d' />
                <Line yAxisId='right' dataKey='difficulty' stroke='#82ca9d' />
              */}
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
    )
  }
}
