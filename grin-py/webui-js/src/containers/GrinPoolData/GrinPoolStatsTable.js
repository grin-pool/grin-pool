import React, { Component } from 'react'
import { Row, Table, Progress } from 'reactstrap'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import _ from 'lodash'
// import { C29_COLOR, C30_COLOR } from '../../constants/styleConstants.js'

export class GrinPoolStatsTableComponent extends Component {
  interval = null

  componentWillUnmount = () => {
    clearInterval(this.interval)
  }

  UNSAFE_componentWillMount () {
    this.fetchGrinPoolTableStats()
    this.interval = setInterval(this.fetchGrinPoolTableStats, 10000)
  }

  fetchGrinPoolTableStats = () => {
    const { fetchNetworkData } = this.props
    fetchNetworkData()
  }

  render () {
    const { historicalGrinPoolData, historicalNetworkData } = this.props
    const grinPoolC29gps = []
    const grinPoolC30gps = []
    historicalGrinPoolData.forEach((blockData) => {
      let c29Stat = 0
      let c30Stat = 0
      blockData.gps.forEach((edgeBit) => {
        if (edgeBit.edge_bits === 29) {
          c29Stat = edgeBit.gps
        } else if (edgeBit.edge_bits === 30) {
          c30Stat = edgeBit.gps
        }
      })
      grinPoolC29gps.push(c29Stat)
      grinPoolC30gps.push(c30Stat)
    })

    const networkC29gps = []
    const networkC30gps = []
    historicalNetworkData.forEach((blockData) => {
      let c29Stat = 0
      let c30Stat = 0
      blockData.gps.forEach((edgeBit) => {
        if (edgeBit.edge_bits === 29) {
          c29Stat = edgeBit.gps
        } else if (edgeBit.edge_bits === 30) {
          c30Stat = edgeBit.gps
        }
      })
      networkC29gps.push(c29Stat)
      networkC30gps.push(c30Stat)
    })

    const grinPoolC29Avg = (_.sum(grinPoolC29gps) / (grinPoolC29gps.length)).toFixed(4)
    const grinPoolC30Avg = (_.sum(grinPoolC30gps) / (grinPoolC30gps.length)).toFixed(4)
    const networkC29Avg = (_.sum(networkC29gps) / (networkC29gps.length)).toFixed(4)
    const networkC30Avg = (_.sum(networkC30gps) / (networkC30gps.length)).toFixed(4)
    const grinPoolC29Percentage = (grinPoolC29Avg / networkC29Avg) * 100
    const grinPoolC30Percentage = (grinPoolC30Avg / networkC30Avg) * 100
    const grinPoolC29Readable = grinPoolC29Percentage.toFixed(2)
    const grinPoolC30Readable = grinPoolC30Percentage.toFixed(2)

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <h4 className='page-title' style={{ marginBottom: 36 }}>{BLOCK_RANGE}-Block Pool Market Share</h4>
        <Table size='sm' responsive hover className='grinPoolStatsTable'>
          <thead>
            <tr>
              <th>Stat</th>
              <th className='center'>Pool</th>
              <th>Network</th>
              <th>Market Share</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope='row'>Average C29 gps</th>
              <td>{grinPoolC29Avg}</td>
              <td>{networkC29Avg}</td>
              <td>{`${grinPoolC29Readable}%`} <Progress color='success' value={grinPoolC29Readable} /></td>
            </tr>
            <tr>
              <th scope='row'>Average C30 gps</th>
              <td>{grinPoolC30Avg}</td>
              <td>{networkC30Avg}</td>
              <td>{`${grinPoolC30Readable}%`} <Progress color='success' value={grinPoolC30Readable} /></td>
            </tr>
          </tbody>
        </Table>
      </Row>
    )
  }
}
