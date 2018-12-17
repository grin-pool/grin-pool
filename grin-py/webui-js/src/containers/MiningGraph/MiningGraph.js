import React, { Component } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, ResponsiveContainer, Legend, Tooltip, ReferenceLine } from 'recharts'

export class MiningGraph extends Component {
  render () {
    const { algorithmData, networkData, poolBlocksMined, color, algorithmNumber } = this.props
    return (
      <ResponsiveContainer width='100%' height={270}>
        <ScatterChart isAnimationActive={false}>
          <XAxis tickCount={7} tickFormatter={(value) => new Date(value * 1000).toLocaleTimeString()} dataKey='timestamp' type={'number'} domain={['dataMin', 'dataMax']} />
          <Legend verticalAlign='top' height={36}/>
          <YAxis tickFormatter={(value) => parseFloat(value).toFixed(2)} yAxisId="left" stroke={color} orientation='left' dataKey={'gps'} type={'number'} domain={['dataMin', 'dataMax']} />
          <Scatter yAxisId="left" fill={color} name={`C${algorithmNumber} Graph Rate`} line data={algorithmData} />
          <Tooltip content={<NetworkDataCustomTooltip />} />
          {networkData.map((block) => {
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
