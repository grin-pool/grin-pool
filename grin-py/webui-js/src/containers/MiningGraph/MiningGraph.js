import React, { Component } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, ResponsiveContainer, Legend, Tooltip, ReferenceLine } from 'recharts'
import { Nav, NavItem, NavLink, TabContent, TabPane } from 'reactstrap'
import classnames from 'classnames'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'
import _ from 'lodash'

export class MiningGraphComponent extends Component {
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
    const { getMinedBlocksAlgos } = this.props
    getMinedBlocksAlgos()
  }

  componentDidUpdate (prevProps) {
    const { latestBlockHeight, getMinedBlocksAlgos } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      getMinedBlocksAlgos()
    }
  }

  render () {
    const { miningData, poolBlocksMined, minedBlockAlgos } = this.props
    // calculations for graphs
    const c29graphRateData = []
    const c31graphRateData = []

    const c29PoolBlocksMined = []
    const c31PoolBlocksMined = []
    poolBlocksMined.forEach((height) => {
      if (_.find(minedBlockAlgos.c29, (item) => item === height)) {
        c29PoolBlocksMined.push(height)
      }
      if (_.find(minedBlockAlgos.c31, (item) => item === height)) {
        c31PoolBlocksMined.push(height)
      }
    })
    let maxC29Gps = 0
    let minC29Gps = 0
    let maxC31Gps = 0
    let minC31Gps = 0
    miningData.forEach((block) => {
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
        if (block.gps[1].gps > maxC31Gps || !maxC31Gps) maxC31Gps = block.gps[1].gps
        if (block.gps[1].gps < minC31Gps || !minC31Gps) minC31Gps = block.gps[1].gps
        c31graphRateData.push({
          height: block.height,
          gps: block.gps[1].gps,
          difficulty: block.difficulty,
          timestamp: block.timestamp
        })
      }
    })

    return (
      <div>
        <Nav tabs>
          <NavItem>
            <NavLink className={classnames({ active: this.state.activeTab === '1' })} onClick={() => { this.toggle('1') }}>
              C29
            </NavLink>
          </NavItem>
          <NavItem>
            <NavLink className={classnames({ active: this.state.activeTab === '2' })} onClick={() => { this.toggle('2') }}>
              C31
            </NavLink>
          </NavItem>
        </Nav>
        <TabContent activeTab={this.state.activeTab}>
          <TabPane tabId='1'>
            <ResponsiveContainer width='100%' height={270}>
              <ScatterChart isAnimationActive={false}>
                <XAxis tickCount={7} tickFormatter={(value) => new Date(value * 1000).toLocaleTimeString()} dataKey='timestamp' type={'number'} domain={['dataMin', 'dataMax']} />
                <Legend verticalAlign='top' height={36}/>
                <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} yAxisId="left" stroke={C29_COLOR} orientation='left' dataKey={'gps'} type={'number'} domain={['dataMin', 'dataMax']} />
                <Scatter yAxisId="left" fill={C29_COLOR} name={`C29 Graph Rate`} line data={c29graphRateData} />
                <Tooltip content={<NetworkDataCustomTooltip />} />
                {miningData.map((block) => {
                  if (c29PoolBlocksMined.indexOf(block.height) > -1) {
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
                <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} yAxisId="left" orientation='left' dataKey={'gps'} type={'number'} domain={['dataMin', 'dataMax']} />
                <Scatter yAxisId="left" fill={C31_COLOR} name={`C31 Graph Rate`} line data={c31graphRateData} />
                <Tooltip content={<NetworkDataCustomTooltip />} />
                {miningData.map((block) => {
                  if (c31PoolBlocksMined.indexOf(block.height) > -1) {
                    return <ReferenceLine key={block.height} yAxisId={'left'} isFront x={block.timestamp} stroke={'#777'} />
                  } else {
                    return null
                  }
                })}
              </ScatterChart>
            </ResponsiveContainer>
          </TabPane>
        </TabContent>
      </div>
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
