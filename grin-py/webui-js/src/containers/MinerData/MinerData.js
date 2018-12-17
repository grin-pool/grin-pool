import React, { Component } from 'react'
import { Row, Col, Table, Nav, NavItem, NavLink, TabContent, TabPane, Alert } from 'reactstrap'
import { C29_COLOR, C30_COLOR } from '../../constants/styleConstants.js'
import { MiningGraph } from '../MiningGraph/MiningGraph.js'
import classnames from 'classnames'

export class MinerDataComponent extends Component {
  constructor (props) {
    super(props)

    this.toggle = this.toggle.bind(this)
    this.state = {
      activeTab: '1'
    }
  }

  toggle (tab) {
    if (this.state.activeTab !== tab) {
      this.setState({
        activeTab: tab
      })
    }
  }

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
    let maxC29Gps = 0
    let minC29Gps = 0
    let maxC30Gps = 0
    let minC30Gps = 0
    const c29graphRateData = []
    const c30graphRateData = []
    minerData.forEach((block) => {
      if (block.gps[0]) {
        if (block.gps[0].gps > maxC29Gps || !maxC29Gps) maxC29Gps = block.gps[0].gps
        if (block.gps[0].gps < minC29Gps || !minC29Gps) minC29Gps = block.gps[0].gps
        c29graphRateData.push({
          height: block.height,
          gps: block.gps[0].gps,
          difficulty: block.difficulty,
          timestamp: block.timestamp
        })
      }
      if (block.gps[1]) {
        if (block.gps[1].gps > maxC30Gps || !maxC30Gps) maxC30Gps = block.gps[1].gps
        if (block.gps[1].gps < minC30Gps || !minC30Gps) minC30Gps = block.gps[1].gps
        c30graphRateData.push({
          height: block.height,
          gps: block.gps[1].gps,
          difficulty: block.difficulty,
          timestamp: block.timestamp
        })
      }
    })
    let c29LatestGraphRate = 'C29 = 0 gps'
    let c30LatestGraphRate = 'C30 = 0 gps'
    if (minerData.length > 0) {
      const lastBlock = minerData[minerData.length - 1]
      if (lastBlock.gps[0]) {
        c29LatestGraphRate = `C${lastBlock.gps[0].edge_bits} = ${lastBlock.gps[0].gps.toFixed(4)} gps`
      }
      if (lastBlock.gps[1]) {
        c30LatestGraphRate = `C${lastBlock.gps[1].edge_bits} = ${lastBlock.gps[1].gps.toFixed(4)} gps`
      }
    } else {
      c29LatestGraphRate = '0 gps'
      c30LatestGraphRate = '0 gps'
    }
    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={5} xl={3}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Miner Stats</h4>
          <Table size='sm'>
            <tbody>
              <tr>
                <td>Graph Rate</td>
                <td><span style={{ color: C29_COLOR }}>{c29LatestGraphRate}</span><br /><span style={{ color: C30_COLOR }}>{c30LatestGraphRate}</span></td>
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
          <Nav tabs>
            <NavItem>
              <NavLink className={classnames({ active: this.state.activeTab === '1' })} onClick={() => { this.toggle('1') }}>
                C29
              </NavLink>
            </NavItem>
            <NavItem>
              <NavLink className={classnames({ active: this.state.activeTab === '2' })} onClick={() => { this.toggle('2') }}>
                C30
              </NavLink>
            </NavItem>
          </Nav>
          <TabContent activeTab={this.state.activeTab}>
            <TabPane tabId='1'>
              <MiningGraph
                color={C29_COLOR}
                networkData={minerData}
                poolBlocksMined={poolBlocksMined}
                algorithmData={c29graphRateData}
                algorithmNumber={'29'}
              />
            </TabPane>
          </TabContent>
          <TabContent activeTab={this.state.activeTab}>
            <TabPane tabId='2'>
              <MiningGraph
                color={C30_COLOR}
                networkData={minerData}
                poolBlocksMined={poolBlocksMined}
                algorithmData={c30graphRateData}
                algorithmNumber={'30'}
              />
            </TabPane>
          </TabContent>
        </Col>
      </Row>
    )
  }
}
