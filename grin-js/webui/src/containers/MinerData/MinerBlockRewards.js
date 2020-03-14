// @flow

import React, { Component } from 'react'
import { Row, Table } from 'reactstrap'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'
import { secondsToHms, getMinerBlockRewardData } from '../../utils/utils.js'
import type { NetworkBlockData, GrinPoolBlockData, MinerShareData } from '../../types'
import ReactTooltip from 'react-tooltip'

export type MinerBlockRewardsStateProps = {
  latestBlockHeight: number,
  recentBlocks: Array<Object>,
  graphTitle: string,
  minerShareData: MinerShareData,
  networkData: Array<NetworkBlockData>,
  grinPoolData: Array<GrinPoolBlockData>
}

export type MinerBlockRewardsDispatchProps = {
  fetchBlockRange: (endBlockHeight?: null | number, rangeSize?: number) => void,
  fetchMinerShareData: () => void,
  fetchNetworkData: () => void,
  fetchGrinPoolData: () => void
}

export type MinerBlockRewardsProps = MinerBlockRewardsStateProps & MinerBlockRewardsDispatchProps

export type MinerBlockRewardsState = {
  range: number
}

export class MinerBlockRewards extends Component<MinerBlockRewardsProps, MinerBlockRewardsState> {
  constructor (props: MinerBlockRewardsProps) {
    super(props)
    this.state = {
      range: 20
    }
  }
  componentDidMount () {
    const { fetchBlockRange } = this.props
    const { range } = this.state
    fetchBlockRange(null, range)
    this.fetchData()
  }

  componentDidUpdate (prevProps: MinerBlockRewardsProps) {
    const { latestBlockHeight } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      this.fetchData()
    }
  }

  fetchData = () => {
    const { fetchBlockRange, fetchNetworkData, fetchGrinPoolData, fetchMinerShareData } = this.props
    const { range } = this.state
    fetchBlockRange(null, range)
    fetchNetworkData()
    fetchGrinPoolData()
    fetchMinerShareData()
  }

  changeRangeSize = (e: Object) => {
    const { fetchBlockRange } = this.props
    const newRange = parseInt(e.target.value)
    fetchBlockRange(null, newRange)
    this.setState({
      range: newRange
    })
  }

  render () {
    const {
      recentBlocks,
      graphTitle,
      minerShareData,
      networkData,
      grinPoolData,
      latestBlockHeight
    } = this.props
    const { range } = this.state
    const rows = []
    // put in order from most recent to oldest
    recentBlocks.sort((b, a) => {
      return b.height - a.height
    })
    if (recentBlocks.length) {
      for (let i = 1; i <= range && i <= recentBlocks.length - 1; i++) {
        const block = recentBlocks[recentBlocks.length - i]
        const currentTimestamp = new Date().getTime()
        const paymentSecondsAgo = currentTimestamp / 1000 - block.timestamp
        const readableTimeAgo = secondsToHms(paymentSecondsAgo)
        const colors = {
          C29: C29_COLOR,
          C31: C31_COLOR
        }
        const rowColor = colors[`C${block.edge_bits}`]
        const uncertainSyntax = block.height > (latestBlockHeight - 1440) ? 'TBD' : 'n/a'
        let minerC29ValidShares = uncertainSyntax
        let minerC31ValidShares = uncertainSyntax
        let poolC29ValidShares = uncertainSyntax
        let poolC31ValidShares = uncertainSyntax
        let minerCredit = uncertainSyntax
        let poolCredit = uncertainSyntax
        let minerPortion = uncertainSyntax
        let userReward
        if (block.height > latestBlockHeight - 1440 + 250 && block.height < latestBlockHeight - 5) {
          const blockRewardData = getMinerBlockRewardData(block.height, networkData, grinPoolData, minerShareData)
          if (blockRewardData) {
            minerC29ValidShares = blockRewardData.cumulativeMinerC29Shares
            minerC31ValidShares = blockRewardData.cumulativeMinerC31Shares
            poolC29ValidShares = blockRewardData.cumulativePoolC29Shares
            poolC31ValidShares = blockRewardData.cumulativePoolC31Shares
            minerCredit = blockRewardData.userCredit
            poolCredit = blockRewardData.poolCredit
            if (!isNaN(poolCredit) && !isNaN(minerCredit)) minerPortion = `${(minerCredit / poolCredit * 100 * 0.98).toFixed(3)}%`
            userReward = blockRewardData.userReward * 0.98
          }
        }
        rows.push(
          <tr key={block.height}>
            <td style={{ textAlign: 'left' }}><a style={{ color: rowColor || C29_COLOR }} href={`https://grinexplorer.net/block/${block.height}`} rel='noopener noreferrer' target='_blank' >{block.height}</a></td>
            <td style={{ color: rowColor }}>C{block.edge_bits}</td>
            <td>{readableTimeAgo} ago</td>
            <td>{block.actual_difficulty || block.total_difficulty}</td>
            <td data-tip='Cumulative number of valid miner C29 shares submitted during 240-block period leading up to block reward'>
              {minerC29ValidShares}<ReactTooltip className={'customTheme'} />
            </td>
            <td data-tip='Cumulative number of total valid pool C29 shares submitted during 240-block period leading up to block reward'>
              {poolC29ValidShares}<ReactTooltip className={'customTheme'} />
            </td>
            <td data-tip='Cumulative number of valid miner C31 shares submitted during 240-block period leading up to block reward'>
              {minerC31ValidShares}<ReactTooltip className={'customTheme'} />
            </td>
            <td data-tip='Cumulative number of total valid pool C31 shares submitted during 240-block period leading up to block reward'>
              {poolC31ValidShares}<ReactTooltip className={'customTheme'} />
            </td>
            <td data-tip='Weight of miner work done during 240-block period leading up to block reward'>
              {minerCredit}<ReactTooltip className={'customTheme'} />
            </td>
            <td data-tip='Weight of total pool work done during 240-block period leading up to block reward'>
              {poolCredit}<ReactTooltip className={'customTheme'} />
            </td>
            <td data-tip='Share of pool credit done by miner during 240-block period leading up to block reward'>
              {minerPortion}<ReactTooltip className={'customTheme'} />
            </td>
            <td style={{ textAlign: 'right' }}>{!isNaN(userReward) ? userReward.toFixed(4) : uncertainSyntax}</td>
          </tr>
        )
      }
    }

    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <div style={{ width: '100%', marginBottom: '14px' }}>
          <h4 className='page-title' style={{ marginBottom: 36, display: 'inline' }}>{graphTitle}  <span style={{ verticalAlign: 'super', fontSize: '0.8rem' }}>Beta</span></h4>
        </div>

        <Table size='sm' responsive hover className={'userRewardsTable'}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }}>Height</th>
              {recentBlocks[0] && recentBlocks[0].edge_bits && <th>Algo</th>}
              <th>Time</th>
              <th>Difficulty</th>
              <th>Miner C29</th>
              <th>Pool C29</th>
              <th>Miner C31</th>
              <th>Pool C31</th>
              <th>Miner Credit</th>
              <th>Pool Credit</th>
              <th>Miner Portion</th>
              <th style={{ textAlign: 'right' }}>Estimated Miner Reward</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </Table>
      </Row>
    )
  }
}
