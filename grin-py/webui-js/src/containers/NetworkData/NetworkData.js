import React, { Component } from 'react'
import { VictoryChart, VictoryLine } from 'victory'

export class NetworkDataComponent extends Component {
  UNSAFE_componentWillMount () {
    setInterval(this.props.fetchNetworkData(), 60000)
  }

  render () {
    const { networkData } = this.props
    const graphRateData = []
    networkData.forEach((block) => {
      graphRateData.push({ x: block.height, y: block.gps })
    })
    return (
      <div>
        <VictoryChart>
          <VictoryLine
            style={{
              data: { stroke: '#c43a31' },
              parent: { border: '1px solid #ccc' }
            }}
            data={graphRateData}
          />
        </VictoryChart>
      </div>
    )
  }
}
