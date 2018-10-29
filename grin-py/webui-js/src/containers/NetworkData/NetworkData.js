import React, { Component } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export class NetworkDataComponent extends Component {
  UNSAFE_componentWillMount () {
    const { fetchNetworkData } = this.props
    fetchNetworkData()
    setInterval(fetchNetworkData, 60000)
  }

  render () {
    const { networkData } = this.props
    const graphRateData = []
    let maxGps
    let minGps
    let maxDifficulty
    let minDifficulty
    networkData.forEach((block) => {
      if (block.gps > maxGps || !maxGps) maxGps = block.gps
      if (block.gps < minGps || !minGps) minGps = block.gps
      if (block.difficulty > maxDifficulty || !maxDifficulty) maxDifficulty = block.difficulty
      if (block.difficulty < minDifficulty || !minDifficulty) minDifficulty = block.difficulty
      graphRateData.push({
        height: block.height,
        gps: block.gps,
        difficulty: block.difficulty
      })
    })

    return (
      <ResponsiveContainer width='100%' height={250}>
        <LineChart data={graphRateData} >
          <XAxis dataKey='height'/>
          <Tooltip />
          <YAxis yAxisId='left' orientation='left' domain={[Math.floor(minGps) - 1, Math.ceil(maxGps) + 1]} allowDecimals={false} />
          <Line yAxisId='left' dataKey='gps' stroke='#8884d8' />
          <YAxis yAxisId='right' orientation='right' domain={[minDifficulty, maxDifficulty]} stroke='#82ca9d' />
          <Line yAxisId='right' dataKey='difficulty' stroke='#82ca9d' />
        </LineChart>
      </ResponsiveContainer>
    )
  }
}
