import React, { Component } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, ResponsiveContainer, Legend, Tooltip, ReferenceLine } from 'recharts'

export class MiningGraph extends Component {
  render () {
    const { algorithmData, miningData, poolBlocksMined, color, algorithmNumber } = this.props
    // calculations for graphs
    const c29graphRateData = []
    const c30graphRateData = []
    let maxC29Gps = 0
    let minC29Gps = 0
    let maxC30Gps = 0
    let minC30Gps = 0
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
    return (
      <ResponsiveContainer width='100%' height={270}>
        <ScatterChart isAnimationActive={false}>
          <XAxis tickCount={7} tickFormatter={(value) => new Date(value * 1000).toLocaleTimeString()} dataKey='timestamp' type={'number'} domain={['dataMin', 'dataMax']} />
          <Legend verticalAlign='top' height={36}/>
          <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} yAxisId="left" stroke={color} orientation='left' dataKey={'gps'} type={'number'} domain={['dataMin', 'dataMax']} />
          <Scatter yAxisId="left" fill={color} name={`C${algorithmNumber} Graph Rate`} line data={algorithmData} />
          <Tooltip content={<NetworkDataCustomTooltip />} />
          {miningData.map((block) => {
            if (poolBlocksMined.indexOf(block.height) > -1) {
              return <ReferenceLine key={block.height} yAxisId={'left'} isFront x={block.timestamp} stroke={'#777'} />
            } else {
              return null
            }
          })}
        </ScatterChart>
      </ResponsiveContainer>
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
