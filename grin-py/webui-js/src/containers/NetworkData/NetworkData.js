import React, { Component } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, ResponsiveContainer, Legend, Tooltip, ReferenceLine } from 'recharts'
import { Row, Col, Table, Nav, NavItem, NavLink, TabContent, TabPane } from 'reactstrap'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { C29_COLOR, C30_COLOR } from '../../constants/styleConstants.js'
import classnames from 'classnames'

export class NetworkDataComponent extends Component {
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
    const c29graphRateData = []
    const c30graphRateData = []
    let maxC29Gps = 0
    let minC29Gps = 0
    let maxC30Gps = 0
    let minC30Gps = 0

    networkData.forEach((block) => {
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
    const c29Floor = Math.floor(minC29Gps)
    const c29Ceiling = Math.ceil(maxC29Gps)
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
              <ResponsiveContainer width='100%' height={270}>
                <ScatterChart isAnimationActive={false}>
                  <XAxis tickCount={7} tickFormatter={(value) => new Date(value * 1000).toLocaleTimeString()} dataKey='timestamp' type={'number'} domain={['dataMin', 'dataMax']} />
                  <Legend verticalAlign='top' height={36}/>
                  <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} yAxisId="left" stroke={C29_COLOR} orientation='left' dataKey={'gps'} type={'number'} domain={[c29Floor, c29Ceiling]} />
                  <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)}yAxisId="right" stroke={C30_COLOR} orientation='right' dataKey={'gps'} type={'number'} domain={['dataMin', 'dataMax']} />
                  {/* <Line dot={false} yAxisId='left' name='C29 (GPU) Graph Rate' dataKey='gps[0].gps' stroke={C29_COLOR} /> */}
                  {/* <Line dot={false} yAxisId='right' name='C30 (ASIC) Graph Rate' dataKey='gps[1].gps' stroke={C30_COLOR} /> */}
                  <Scatter yAxisId="left" fill={C29_COLOR} name='C29 (GPU) Graph Rate' line data={c29graphRateData} />
                  <Scatter yAxisId="right" fill={C30_COLOR} name='C30 (ASIC) Graph Rate' line data={c30graphRateData} />
                  <Tooltip content={<NetworkDataCustomTooltip />} />
                  {/* <YAxis yAxisId='right' orientation='right' domain={[minDifficulty, maxDifficulty]} stroke='#82ca9d' />
                    <Line yAxisId='right' dataKey='difficulty' stroke='#82ca9d' />
                  */}
                  {networkData.map((block) => {
                    if (poolBlocksMined.indexOf(block.height) > -1) {
                      return <ReferenceLine key={block.height} yAxisId={'left'} isFront x={block.timestamp} stroke={'#777'} />
                    } else {
                      return null
                    }
                  })}
                </ScatterChart>
              </ResponsiveContainer>
            </TabPane>
          </TabContent>
          <TabContent activeTab={this.state.activeTab}>
            <TabPane tabId='2'>
              <ResponsiveContainer width='100%' height={270}>
                <ScatterChart isAnimationActive={false}>
                  <XAxis tickCount={7} tickFormatter={(value) => new Date(value * 1000).toLocaleTimeString()} dataKey='timestamp' type={'number'} domain={['dataMin', 'dataMax']} />
                  <Legend verticalAlign='top' height={36}/>
                  <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} yAxisId="left" stroke={C29_COLOR} orientation='left' dataKey={'gps'} type={'number'} domain={[c29Floor, c29Ceiling]} />
                  <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)}yAxisId="right" stroke={C30_COLOR} orientation='right' dataKey={'gps'} type={'number'} domain={['dataMin', 'dataMax']} />
                  {/* <Line dot={false} yAxisId='left' name='C29 (GPU) Graph Rate' dataKey='gps[0].gps' stroke={C29_COLOR} /> */}
                  {/* <Line dot={false} yAxisId='right' name='C30 (ASIC) Graph Rate' dataKey='gps[1].gps' stroke={C30_COLOR} /> */}
                  <Scatter yAxisId="left" fill={C29_COLOR} name='C29 (GPU) Graph Rate' line data={c29graphRateData} />
                  <Scatter yAxisId="right" fill={C30_COLOR} name='C30 (ASIC) Graph Rate' line data={c30graphRateData} />
                  <Tooltip content={<NetworkDataCustomTooltip />} />
                  {/* <YAxis yAxisId='right' orientation='right' domain={[minDifficulty, maxDifficulty]} stroke='#82ca9d' />
                    <Line yAxisId='right' dataKey='difficulty' stroke='#82ca9d' />
                  */}
                  {networkData.map((block) => {
                    if (poolBlocksMined.indexOf(block.height) > -1) {
                      return <ReferenceLine key={block.height} yAxisId={'left'} isFront x={block.timestamp} stroke={'#777'} />
                    } else {
                      return null
                    }
                  })}
                </ScatterChart>
              </ResponsiveContainer>
            </TabPane>
          </TabContent>

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
