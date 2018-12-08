import React, { Component } from 'react'
import { Row, Table, Progress } from 'reactstrap'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import _ from 'lodash'
// import { C29_COLOR, C30_COLOR } from '../../constants/styleConstants.js'

export class GrinPoolStatsTableComponent extends Component {
  UNSAFE_componentWillMount () {
    this.fetchGrinPoolTableStats()
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      this.fetchGrinPoolTableStats()
    }
  }

  fetchGrinPoolTableStats = () => {
    const { fetchNetworkData } = this.props
    fetchNetworkData()
  }

  render () {
    const { historicalGrinPoolData, historicalNetworkData } = this.props
    if (historicalNetworkData.length === 0) return null
    let c29Share = 0
    let c30Share = 0
    let poolBlock29Rate = 0
    let poolBlock30Rate = 0
    let networkBlock29Rate = 0
    let networkBlock30Rate = 0

    const poolBlockIndex = historicalGrinPoolData.length - 1
    const poolBlock = historicalGrinPoolData[poolBlockIndex]
    if (historicalGrinPoolData[poolBlockIndex]) {
      const poolBlock29Data = _.find(poolBlock.gps, (graph) => graph.edge_bits === 29)
      const poolBlock30Data = _.find(poolBlock.gps, (graph) => graph.edge_bits === 30)
      if (poolBlock29Data) {
        poolBlock29Rate = poolBlock29Data.gps.toFixed(2)
      }
      if (poolBlock30Data) {
        poolBlock30Rate = poolBlock30Data.gps.toFixed(2)
      }

      const networkBlockIndex = historicalNetworkData.length - 1
      const networkBlock = historicalNetworkData[networkBlockIndex]
      const networkBlock29Data = _.find(networkBlock.gps, (graph) => graph.edge_bits === 29)
      const networkBlock30Data = _.find(networkBlock.gps, (graph) => graph.edge_bits === 30)
      networkBlock29Rate = networkBlock29Data ? networkBlock29Data.gps.toFixed(2) : 0
      networkBlock30Rate = networkBlock30Data ? networkBlock30Data.gps.toFixed(2) : 0

      c29Share = (poolBlock29Rate / networkBlock29Rate * 100).toFixed(2)
      c30Share = (poolBlock30Rate / networkBlock30Rate * 100).toFixed(2)
    }

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
              <td>{poolBlock29Rate}</td>
              <td>{networkBlock29Rate}</td>
              <td>{`${c29Share} %`} <Progress color='success' value={c29Share} /></td>
            </tr>
            <tr>
              <th scope='row'>Average C30 gps</th>
              <td>{poolBlock30Rate}</td>
              <td>{networkBlock30Rate}</td>
              <td>{!isNaN(c30Share) ? `${c30Share} %` : 'n/a'} <Progress color='success' value={c30Share} /></td>
            </tr>
          </tbody>
        </Table>
      </Row>
    )
  }
}
