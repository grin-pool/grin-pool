import React, { Component } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, ResponsiveContainer, Legend, Tooltip, ReferenceLine } from 'recharts'
import { Nav, NavItem, NavLink, TabContent, TabPane } from 'reactstrap'
import classnames from 'classnames'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'

export class MiningGraphComponent extends Component {
  constructor (props) {
    super(props)

    this.toggle = this.toggle.bind(this)
    this.state = {
      activeTab: '1'
    }
  }

  toggle (tab) {
    console.log('this.state.activeTab is: ', this.state.activeTab, ' and tab is: ', tab)
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
    const { miningData, poolBlocksMined } = this.props
    // calculations for graphs
    const graphRateData = {}

    miningData.forEach((block) => {
      if (block.gps) {
        block.gps.forEach((algo) => {
          if (!graphRateData[`C${algo.edge_bits}`]) {
            graphRateData[`C${algo.edge_bits}`] = []
          }
          graphRateData[`C${algo.edge_bits}`].push({
            difficulty: block.difficulty,
            gps: algo.gps,
            height: block.height,
            timestamp: block.timestamp
          })
        })
      }
    })
    const COLORS = {
      C29: C29_COLOR,
      C31: C31_COLOR
    }
    const algos = Object.keys(graphRateData)
    let graphIterator = 0
    let tabIterator = 0
    return (
      <div>
        <Nav tabs>
          {algos.map((algo, iterator) => {
            tabIterator++
            console.log('algo is: ', algo, ' tabIterator is: ', iterator + 1)
            if (tabIterator === 1) {
              if (algo !== 'C29') console.log('p[roblem')
            } else {
              if (algo !== 'C31') console.log('problem')
            }
            return (
              <NavItem key={algo}>
                <NavLink
                  className={classnames({ active: this.state.activeTab === `${iterator + 1}` })}
                  onClick={() => { this.toggle(`${iterator + 1}`) }}
                  style={{ cursor: 'pointer' }}
                >
                  {algo}
                </NavLink>
              </NavItem>
            )
          })}
        </Nav>
        {algos.map((algo, index) => {
          graphIterator++
          return (
            <TabContent activeTab={this.state.activeTab} key={graphIterator}>
              <TabPane tabId={`${graphIterator}`}>
                <ResponsiveContainer width='100%' height={270}>
                  <ScatterChart isAnimationActive={false}>
                    <XAxis tickCount={7} tickFormatter={(value) => new Date(value * 1000).toLocaleTimeString()} dataKey='timestamp' type={'number'} domain={['dataMin', 'dataMax']} />
                    <Legend verticalAlign='top' height={36}/>
                    <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} yAxisId="left" stroke={COLORS[algo]} orientation='left' dataKey={'gps'} type={'number'} domain={['dataMin', 'dataMax']} />
                    <Scatter yAxisId="left" fill={COLORS[algo]} name={`${algo} Graph Rate`} line data={graphRateData[algo]} />
                    <Tooltip content={<NetworkDataCustomTooltip />} />
                    {miningData.map((block) => {
                      if (poolBlocksMined[`${algo.toLowerCase()}`].indexOf(block.height) > -1) {
                        return <ReferenceLine key={block.height} yAxisId={'left'} isFront x={block.timestamp} stroke={'#777'} />
                      } else {
                        return null
                      }
                    })}
                  </ScatterChart>
                </ResponsiveContainer>
              </TabPane>
            </TabContent>
          )
        })}
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
