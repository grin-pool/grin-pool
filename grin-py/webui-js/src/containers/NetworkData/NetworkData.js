import React, { Component } from 'react'
import { Row, Col, Table } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { C29_COLOR, C30_COLOR } from '../../constants/styleConstants.js'
import { MiningGraph } from '../MiningGraph/MiningGraph.js'

export class NetworkDataComponent extends Component {
  UNSAFE_componentWillMount () {
    const { fetchNetworkData } = this.props
    fetchNetworkData()
  }

  componentDidUpdate (prevProps) {
    const { latestBlock, fetchNetworkData } = this.props
    if (latestBlock.height !== prevProps.latestBlock.height) {
      fetchNetworkData()
    }
  }

  render () {
    const { networkData, latestBlock, poolBlocksMined } = this.props

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
          <Table size='sm'>
            <tbody>
              <tr>
                <td id='box'><FontAwesomeIcon style={{ marginRight: 5 }} size='lg' icon={'chart-line'} /> Graph Rate</td>
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
          <MiningGraph
            miningData={networkData}
            poolBlocksMined={poolBlocksMined}
          />
        </Col>
      </Row>
    )
  }
}

export class AnimatedText {
  render () {
    return (
      <span>{this.props.children}</span>
    )
  }
}

export class NetworkDataCustomTooltip extends Component {
  render () {
    const { active } = this.props

    if (active) {
      const { payload } = this.props
      return (
        <div className="custom-network-data-tooltip">
          <p>Block: {payload[0].payload.height}</p>
          <p>Timestamp: {payload[0].payload.timestamp}</p>
          <p>Time: {new Date(payload[0].payload.timestamp * 1000).toLocaleTimeString()}</p>
          <p>GPS: {payload[0].payload.gps}</p>
        </div>
      )
    }

    return null
  }
}
