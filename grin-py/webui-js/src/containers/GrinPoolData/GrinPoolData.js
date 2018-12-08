import React, { Component } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, ReferenceDot } from 'recharts'
import { Row, Col, Table } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { C29_COLOR, C30_COLOR } from '../../constants/styleConstants.js'

export class GrinPoolDataComponent extends Component {
  interval = null

  componentWillUnmount = () => {
    clearInterval(this.interval)
  }

  UNSAFE_componentWillMount () {
    this.fetchGrinPoolData()
    this.interval = setInterval(this.fetchGrinPoolData, 10000)
  }

  fetchGrinPoolData = () => {
    const { fetchNetworkData, fetchGrinPoolLastBlock } = this.props
    fetchNetworkData()
    fetchGrinPoolLastBlock()
  }

  render () {
    const { networkData, activeWorkers, lastBlockMined, poolBlocksMined } = this.props
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
    if (networkData.length > 0) {
      const lastBlock = networkData[networkData.length - 1]
      if (lastBlock.gps[0]) {
        c29LatestGraphRate = `C${lastBlock.gps[0].edge_bits} = ${lastBlock.gps[0].gps.toFixed(2)} gps`
      }
      if (lastBlock.gps[1]) {
        c30LatestGraphRate = `C${lastBlock.gps[1].edge_bits} = ${lastBlock.gps[1].gps.toFixed(2)} gps`
      }
    } else {
      c29LatestGraphRate = '0 gps'
      c30LatestGraphRate = '0 gps'
    }
    const nowTimestamp = Date.now()
    const lastBlockTimeAgo = Math.floor(nowTimestamp / 1000 - lastBlockMined)
    const totalPoolBlocksMined = networkData[networkData.length - 1] ? networkData[networkData.length - 1].total_blocks_found : 0
    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>GRIN-Pool Stats</h4>
          <Table size='sm'>
            <tbody>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'chart-line'} /> Graph Rate</td>
                <td><span style={{ color: C29_COLOR }}>{c29LatestGraphRate}</span><br /><span style={{ color: C30_COLOR }}>{c30LatestGraphRate}</span></td>
              </tr>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'clock'} /> Block Found</td>
                <td>{lastBlockTimeAgo} sec ago</td>
              </tr>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'desktop'} />Active Miners</td>
                <td>{activeWorkers}</td>
              </tr>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'link'} />Blocks Found</td>
                <td>{totalPoolBlocksMined}</td>
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
              {networkData.map((block) => {
                if (poolBlocksMined.indexOf(block.height) > -1) {
                  return <ReferenceDot key={block.height} yAxisId={'left'} r={4} isFront x={block.height} y={block.gps[0].gps} fill={C29_COLOR} stroke={C29_COLOR} />
                } else {
                  return null
                }
              })}
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
    )
  }
}
