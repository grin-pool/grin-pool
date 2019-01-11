import React, { Component } from 'react'
import { Row, Col, Table, Alert } from 'reactstrap'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'
import { MiningGraphConnector } from '../../redux/connectors/MiningGraphConnector.js'
import { nanoGrinToGrin } from '../../utils/utils.js'

export class MinerDataComponent extends Component {
  constructor (props) {
    super(props)
    this.state = {
      faderStyleId: 'blockHeight1'
    }
  }

  UNSAFE_componentWillMount () {
    this.updateData()
  }

  componentDidUpdate (prevProps) {
    const { faderStyleId } = this.state
    const { latestBlockHeight } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      this.updateData()
      this.setState({
        faderStyleId: faderStyleId === 'blockHeight1' ? 'blockHeight2' : 'blockHeight1'
      })
    }
  }

  updateData = () => {
    const { fetchMinerData, fetchLatestBlockGrinEarned } = this.props
    fetchMinerData()
    fetchLatestBlockGrinEarned()
  }

  render () {
    const { minerData, poolBlocksMined, latestBlockGrinEarned, latestBlock } = this.props
    const { faderStyleId } = this.state
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
    const nowTimestamp = Date.now()
    const latestBlockTimeAgo = latestBlock.timestamp ? Math.floor((nowTimestamp / 1000) - latestBlock.timestamp) : ''
    const latestBlockGrinEarnedSyntax = (!isNaN(latestBlockGrinEarned) && latestBlockGrinEarned > 0) ? `~ ${nanoGrinToGrin(latestBlockGrinEarned).toFixed(6)} GRIN` : 'n/a'
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
                <td>Chain Height</td>
                <td id={faderStyleId}>{latestBlock.height}</td>
              </tr>
              <tr>
                <td>Latest Block Earning</td>
                <td>{latestBlockGrinEarnedSyntax}</td>
              </tr>
              <tr>
                <td>Last Block Found</td>
                <td>{latestBlockTimeAgo} sec ago</td>
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
