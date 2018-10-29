import React, { Component } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Row, Col, Table } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

export class NetworkDataComponent extends Component {
  UNSAFE_componentWillMount () {
    const { fetchNetworkData } = this.props
    fetchNetworkData()
    setInterval(fetchNetworkData, 10000)
  }

  render () {
    const { networkData, latestBlock } = this.props
    const graphRateData = []
    let maxGps
    let minGps
    let maxDifficulty
    let minDifficulty
    networkData.forEach((block) => {
      if (block.gps > maxGps || !maxGps) maxGps = block.gps
      if (block.gps < minGps || !minGps) minGps = block.gps
      if (block.difficulty > maxDifficulty || !maxDifficulty) maxDifficulty = block.difficulty
      if (block.difficulty < minDifficulty || !minDifficulty) minDifficulty = block.difficulty
      graphRateData.push({
        height: block.height,
        gps: block.gps,
        difficulty: block.difficulty
      })
    })
    let latestGraphRate, latestDifficulty, latestBlockHeight
    if (networkData.length > 0) {
      const lastBlock = networkData[networkData.length - 1]
      latestGraphRate = lastBlock.gps
      latestDifficulty = lastBlock.difficulty
      latestBlockHeight = lastBlock.height
    } else {
      latestGraphRate = 0
      latestDifficulty = 0
      latestBlockHeight = 0
    }
    const nowTimestamp = Date.now()
    const latestBlockTimeAgo = latestBlock.timestamp ? Math.floor((nowTimestamp / 1000) - latestBlock.timestamp) : ''
    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={3} lg={3} xl={3}>
          <Table>
            <tbody>
              <tr>
                <td><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'chart-line'} /> Graph Rate</td>
                <td>{latestGraphRate} g/s</td>
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
                <td>60 grin / block</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={9} lg={9} xl={9}>
          <ResponsiveContainer width='100%' height={250}>
            <LineChart data={graphRateData} >
              <XAxis dataKey='height'/>
              <Tooltip />
              <YAxis yAxisId='left' orientation='left' domain={[Math.floor(minGps) - 1, Math.ceil(maxGps) + 1]} allowDecimals={false} />
              <Line yAxisId='left' dataKey='gps' stroke='#8884d8' />
              <YAxis yAxisId='right' orientation='right' domain={[minDifficulty, maxDifficulty]} stroke='#82ca9d' />
              <Line yAxisId='right' dataKey='difficulty' stroke='#82ca9d' />
            </LineChart>
          </ResponsiveContainer>
        </Col>
      </Row>
    )
  }
}
