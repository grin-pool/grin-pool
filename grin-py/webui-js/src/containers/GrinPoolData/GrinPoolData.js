import React, { Component } from 'react'
import { Row, Col, Table } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { C29_COLOR, C30_COLOR } from '../../constants/styleConstants.js'
import { MiningGraph } from '../MiningGraph/MiningGraph.js'

export class GrinPoolDataComponent extends Component {
  interval = null

  componentWillUnmount = () => {
    clearInterval(this.interval)
  }

  UNSAFE_componentWillMount () {
    this.fetchGrinPoolData()
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      this.fetchGrinPoolData()
    }
  }

  fetchGrinPoolData = () => {
    const { fetchGrinPoolData, fetchGrinPoolLastBlock } = this.props
    fetchGrinPoolData()
    fetchGrinPoolLastBlock()
  }

  render () {
    const { grinPoolData, activeWorkers, lastBlockMined, poolBlocksMined } = this.props

    let c29LatestGraphRate = 'C29 = 0 gps'
    let c30LatestGraphRate = 'C30 = 0 gps'
    if (grinPoolData.length > 0) {
      const lastBlock = grinPoolData[grinPoolData.length - 1]
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
    const totalPoolBlocksMined = grinPoolData[grinPoolData.length - 1] ? grinPoolData[grinPoolData.length - 1].total_blocks_found : 0

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
          <MiningGraph
            miningData={grinPoolData}
            poolBlocksMined={poolBlocksMined}
          />
        </Col>
      </Row>
    )
  }
}
