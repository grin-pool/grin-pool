import React, { Component } from 'react'
import { Row, Col, Table, Alert } from 'reactstrap'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'
import { MiningGraphConnector } from '../../redux/connectors/MiningGraphConnector.js'

export class MinerDataComponent extends Component {
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
    const { fetchMinerData } = this.props
    fetchMinerData()
  }

  render () {
    const { minerData, poolBlocksMined } = this.props
    const numberOfRecordedBlocks = minerData.length
    const noBlocksAlertSyntax = 'Mining data may take a few minutes to show up after you start mining'

    let c29LatestGraphRate = 'C29 = 0 gps'
    let c31LatestGraphRate = 'C31 = 0 gps'
    if (minerData.length > 0) {
      const lastBlock = minerData[minerData.length - 1]
      if (lastBlock.gps[0]) {
        c29LatestGraphRate = `C${lastBlock.gps[0].edge_bits} = ${lastBlock.gps[0].gps.toFixed(4)} gps`
      }
      if (lastBlock.gps[1]) {
        c31LatestGraphRate = `C${lastBlock.gps[1].edge_bits} = ${lastBlock.gps[1].gps.toFixed(4)} gps`
      }
    } else {
      c29LatestGraphRate = '0 gps'
      c31LatestGraphRate = '0 gps'
    }
    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Miner Stats</h4>
          <Table size='sm'>
            <tbody>
              <tr>
                <td>Graph Rate</td>
                <td><span style={{ color: C29_COLOR }}>{c29LatestGraphRate}</span><br /><span style={{ color: C31_COLOR }}>{c31LatestGraphRate}</span></td>
              </tr>
              <tr>
                <td>Block Found</td>
                <td>Test</td>
              </tr>
              <tr>
                <td>Blocks Found</td>
                <td>Test</td>
              </tr>
            </tbody>
          </Table>
        </Col>
        <Col xs={12} md={12} lg={7} xl={9}>
          <h4 className='page-title'>Graph Rate</h4>
          <div style={{ textAlign: 'center', marginBottom: 12 }}>{(numberOfRecordedBlocks === 0) && <Alert color='warning' style={{ textAlign: 'center', display: 'inline' }}>{noBlocksAlertSyntax}</Alert>}</div>
          <MiningGraphConnector
            miningData={minerData}
            poolBlocksMined={poolBlocksMined}
          />
        </Col>
      </Row>
    )
  }
}
