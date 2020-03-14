// @flow

import React, { Component } from 'react'
import { Row, Col, Table, Alert } from 'reactstrap'
import { C29_COLOR, C31_COLOR } from '../../custom/custom.js'
import { MiningGraphConnector } from '../../redux/connectors/MiningGraphConnector.js'
import { nanoGrinToGrin, calculateDailyEarningFromGps } from '../../utils/utils.js'
import { BLOCK_RANGE } from '../../constants/dataConstants.js'
import { type MinerBlockData } from '../../types.js'
import ReactTooltip from 'react-tooltip'

export type MinerDataComponentStateProps = {
    minerData: MinerBlockData,
    latestBlockHeight: number,
    poolBlocksMined: { c29: Array<number>, c31: Array<number>},
    latestBlockGrinEarned: number,
    latestBlock: Object,
    amount: number,
    minerImmatureBalance: number,
    totalPayoutsAmount: number,
    minerShareData: Object,
    networkData: Array<Object>,
    grinPoolData: Array<Object>,
    grinPoolRecentBlocks: Array<Object>
}

export type MinerDataComponentDispatchProps = {
    fetchMinerData: () => void,
    fetchMinerPaymentData: () => void,
    fetchMinerImmatureBalance: () => void,
    getLatestMinerPaymentRange: () => void,
    fetchMinerShareData: () => void,
    fetchNetworkData: () => void,
    fetchGrinPoolData: () => void,
    fetchGrinPoolRecentBlocks: () => void
}

export type MinerDataComponentProps = MinerDataComponentDispatchProps & MinerDataComponentStateProps

type MinerDataComponentState = {
  faderStyleId: string,
  matureBalanceStyleId: string,
  immatureBalanceStyleId: string
}

export class MinerDataComponent extends Component<MinerDataComponentProps, MinerDataComponentState> {
  constructor (props: MinerDataComponentProps) {
    super(props)
    this.state = {
      faderStyleId: 'blockHeight1',
      matureBalanceStyleId: 'balance1',
      immatureBalanceStyleId: 'balance1'
    }
  }

  UNSAFE_componentWillMount () {
    this.updateData()
  }

  componentDidUpdate (prevProps: MinerDataComponentProps) {
    const { faderStyleId, matureBalanceStyleId, immatureBalanceStyleId } = this.state
    const { latestBlockHeight, amount, minerImmatureBalance } = this.props
    if (prevProps.latestBlockHeight !== latestBlockHeight) {
      console.log('Block heights: ', prevProps.latestBlockHeight, ' vs. ', latestBlockHeight)
      this.updateData()
      this.setState({
        faderStyleId: faderStyleId === 'blockHeight1' ? 'blockHeight2' : 'blockHeight1'
      })
    }
    if (prevProps.amount < amount) {
      this.setState({
        matureBalanceStyleId: matureBalanceStyleId === 'balance1' ? 'balance2' : 'balance1'
      })
    }
    if (prevProps.minerImmatureBalance < minerImmatureBalance) {
      this.setState({
        immatureBalanceStyleId: immatureBalanceStyleId === 'balance1' ? 'balance2' : 'balance1'
      })
    }
  }

  updateData = () => {
    const {
      fetchMinerData,
      fetchMinerShareData,
      fetchMinerPaymentData,
      fetchMinerImmatureBalance,
      getLatestMinerPaymentRange,
      fetchNetworkData,
      fetchGrinPoolData,
      fetchGrinPoolRecentBlocks,
      fetchMinerLatestBlockReward,
      fetchMinerNextBlockReward
    } = this.props
    fetchMinerData()
    fetchMinerPaymentData()
    fetchMinerImmatureBalance()
    getLatestMinerPaymentRange()
    fetchMinerShareData()
    fetchNetworkData()
    fetchGrinPoolData()
    fetchGrinPoolRecentBlocks()
    fetchMinerLatestBlockReward()
    fetchMinerNextBlockReward()
    console.log('UPDATING MINER DATA')
  }

  render () {
    const {
      minerData,
      poolBlocksMined,
      latestBlock,
      amount,
      minerImmatureBalance,
      totalPayoutsAmount,
      networkData,
      grinPoolData,
      grinPoolRecentBlocks,
      nextBlockGrinEarned,
      latestBlockGrinEarned
    } = this.props
    const { faderStyleId, matureBalanceStyleId, immatureBalanceStyleId } = this.state
    const numberOfRecordedBlocks = minerData.length
    const noBlocksAlertSyntax = 'Mining data may up to 5 blocks to show up after you start mining'

    let maxPoolBlockHeight = 0
    grinPoolData.forEach(block => {
      if (block.height > maxPoolBlockHeight) maxPoolBlockHeight = block.height
    })
    let grinPoolLatestBlock = 0
    grinPoolRecentBlocks.forEach(block => {
      if (block.height > grinPoolLatestBlock && block.height < maxPoolBlockHeight) grinPoolLatestBlock = block.height
    })

    let c29LatestGraphRate = 0
    let c31LatestGraphRate = 0
    if (minerData.length > 0) {
      const lastBlock = minerData[minerData.length - 1]
      const c29LatestEntry = lastBlock.gps.find((item) => item.edge_bits === 29)
      if (c29LatestEntry) c29LatestGraphRate = c29LatestEntry.gps.toFixed(2)
      const c31LatestEntry = lastBlock.gps.find((item) => item.edge_bits === 31)
      if (c31LatestEntry) c31LatestGraphRate = c31LatestEntry.gps.toFixed(2)
    }
    const graphRates = {
      c29: [],
      c31: []
    }
    const payWindowAverage = { c29: [], c31: [] }
    minerData.forEach((block) => {
      if (block.gps) {
        if (block.height >= latestBlock.height - 245 && block.height < latestBlock.height - 5) {
          block.gps.forEach((algo) => {
            payWindowAverage[`c${algo.edge_bits}`].push(algo.gps)
          })
        }
        block.gps.forEach((algo) => {
          graphRates[`c${algo.edge_bits}`].push(algo.gps)
        })
      }
    })
    const c29PayWindowAverage = payWindowAverage.c29.length ? (payWindowAverage.c29.reduce((a, b) => a + b, 0) / 240).toFixed(2) : 0
    const c31PayWindowAverage = payWindowAverage.c31.length ? (payWindowAverage.c31.reduce((a, b) => a + b, 0) / 240).toFixed(2) : 0
    const c29Average = graphRates.c29.length ? (graphRates.c29.reduce((a, b) => a + b, 0) / 1440).toFixed(2) : 0
    const c31Average = graphRates.c31.length ? (graphRates.c31.reduce((a, b) => a + b, 0) / 1440).toFixed(2) : 0
    const nowTimestamp = Date.now()
    const latestBlockTimeAgo = latestBlock.timestamp ? Math.floor((nowTimestamp / 1000) - latestBlock.timestamp) : ''
    const mergedPoolBlocksMined = poolBlocksMined.c29.concat(poolBlocksMined.c31)
    let latestBlockGrinEarnedSyntax
    if (typeof latestBlockGrinEarned === 'number' && latestBlockGrinEarned > 0) {
      latestBlockGrinEarnedSyntax = `${(nanoGrinToGrin(latestBlockGrinEarned) * 0.98).toFixed(4)} GRIN`
    } else if (latestBlock.height - Math.max(...mergedPoolBlocksMined) < 1) {
      latestBlockGrinEarnedSyntax = 'Calculating...'
    } else {
      latestBlockGrinEarnedSyntax = 'n/a'
    }
    const readableAmount = amount > 0 ? nanoGrinToGrin(amount).toFixed(4) : 0
    const minerImmatureBalanceSyntax = (!isNaN(minerImmatureBalance) && minerImmatureBalance > 0) ? `${nanoGrinToGrin(minerImmatureBalance * 0.98).toFixed(4)} GRIN` : 'n/a'
    const latestSecondaryScaling = latestBlock.secondary_scaling
    const c29Scale = Math.max(29, latestSecondaryScaling)
    const c31Scale = Math.pow(2, (31 - 23)) * 31 // 7936
    const c29To31Strength = c29Scale / c31Scale // per share, not per gps
    let c29AverageEquivalence, c31AverageEquivalence
    if (c29To31Strength && !isNaN(c29To31Strength)) {
      const c29AverageEquivalencePrecise = ((parseFloat(c29Average)) + (parseFloat(c31Average) / c29To31Strength))
      const c31AverageEquivalencePrecise = ((parseFloat(c29Average) * c29To31Strength) + (parseFloat(c31Average)))
      c29AverageEquivalence = c29AverageEquivalencePrecise.toFixed(2)
      c31AverageEquivalence = c31AverageEquivalencePrecise.toFixed(2)
    }
    const nextBlockRewardSyntax = typeof nextBlockGrinEarned === 'number' ? `${(nanoGrinToGrin(nextBlockGrinEarned) * 0.98).toFixed(4)} GRIN` : 'n/a'
    const estimatedDailyEarningsFromGps = calculateDailyEarningFromGps(networkData, minerData, latestBlock.height)
    const estimatedDailyEarningsSyntax = isNaN(estimatedDailyEarningsFromGps) ? 'n/a' : `${(estimatedDailyEarningsFromGps * 0.98).toFixed(4)} GRIN`
    return (
      <Row xs={12} md={12} lg={12} xl={12}>
        <Col xs={12} md={12} lg={12} xl={12}>
          <h4 className='page-title'>Graph Rate</h4>
          <div style={{ textAlign: 'center', marginBottom: 12 }}>{(numberOfRecordedBlocks === 0) && <Alert color='warning' style={{ textAlign: 'center', display: 'inline' }}>{noBlocksAlertSyntax}</Alert>}</div>
          <MiningGraphConnector
            miningData={minerData}
            poolBlocksMined={poolBlocksMined}
            decimals={2}
          />
        </Col>
        <Col xs={12} md={12} lg={12} xl={12}>
          <h4 className='page-title' style={{ marginBottom: 36 }}>Total Miner Stats</h4>
          <Row>
            <Col xs={12} md={6} lg={6} xl={6}>
              <Table size='sm'>
                <tbody>
                  <tr>
                    <td>Current Graph Rate</td>
                    <td><span style={{ color: C29_COLOR }}>C29: {c29LatestGraphRate} gps</span><br /><span style={{ color: C31_COLOR }}>C31: {c31LatestGraphRate} gps</span></td>
                  </tr>
                  <tr>
                    <td>Chain Height</td>
                    <td id={faderStyleId}>{latestBlock.height}</td>
                  </tr>
                  <tr>
                    <td>Last Network Block</td>
                    <td>{latestBlockTimeAgo} sec ago</td>
                  </tr>
                  <tr>
                    <td>Miner 240-Block Average <span data-tip={`When mining during the past 240 blocks, these graph rates are what you have averaged `} style={{ verticalAlign: 'super', fontSize: '0.8rem' }}>?</span><ReactTooltip className={'customTheme'} /></td>
                    <td><span style={{ color: C29_COLOR }}>C29: {c29PayWindowAverage} gps</span><br /><span style={{ color: C31_COLOR }}>C31: {c31PayWindowAverage} gps</span></td>
                  </tr>
                  <tr>
                    <td>Miner {BLOCK_RANGE}-Block Average <span data-tip={`When mining during the past ${BLOCK_RANGE} blocks, these graph rates are what you have averaged `} style={{ verticalAlign: 'super', fontSize: '0.8rem' }}>?</span><ReactTooltip className={'customTheme'} /></td>
                    <td><span style={{ color: C29_COLOR }}>C29: {c29Average} gps</span><br /><span style={{ color: C31_COLOR }}>C31: {c31Average} gps</span></td>
                  </tr>
                  <tr>
                    <td>Miner {BLOCK_RANGE}-Block Average Equivalence <span data-tip='The estimated gps you would need of each algorithm to earn an equivalent amount of GRIN based on your average gps' style={{ verticalAlign: 'super', fontSize: '0.8rem' }}>?</span><ReactTooltip className={'customTheme'} /></td>
                    <td><span style={{ color: C29_COLOR }}>C29: {c29AverageEquivalence} gps</span><br /><span style={{ color: C31_COLOR }}>C31: {c31AverageEquivalence} gps</span></td>
                  </tr>
                </tbody>
              </Table>
            </Col>
            <Col xs={12} md={6} lg={6} xl={6}>
              <Table size='sm'>
                <tbody>
                  <tr className={'betaEstimates'}>
                    <td>Estimated Share of Last Pool Block <span data-tip='Your estimated share of the last pool block, based on your work done during 240-block period leading up to block reward' style={{ verticalAlign: 'super', fontSize: '0.8rem' }}>?</span><ReactTooltip className={'customTheme'} /></td>
                    <td>{latestBlockGrinEarnedSyntax}</td>
                  </tr>
                  <tr className={'betaEstimates'}>
                    <td>Estimated Share of Next Pool Block <span data-tip='Your estimated share of the next pool block, based on your work done during the past 240 blocks' style={{ verticalAlign: 'super', fontSize: '0.8rem' }}>?</span><ReactTooltip className={'customTheme'} /></td>
                    <td>{nextBlockRewardSyntax}</td>
                  </tr>
                  <tr className={'betaEstimates'}>
                    <td>Estimated Average Daily Earnings <span data-tip='Your estimated daily earnings based on your work done during the past 240 blocks' style={{ verticalAlign: 'super', fontSize: '0.8rem' }}>?</span><ReactTooltip className={'customTheme'} /></td>
                    <td>{estimatedDailyEarningsSyntax}</td>
                  </tr>
                  <tr>
                    <td>Available Balance</td>
                    <td id={matureBalanceStyleId}>{readableAmount} GRIN</td>
                  </tr>
                  <tr>
                    <td>Immature Balance</td>
                    <td id={immatureBalanceStyleId}>{minerImmatureBalanceSyntax}</td>
                  </tr>
                  <tr>
                    <td>Total Payouts</td>
                    <td>{nanoGrinToGrin(totalPayoutsAmount).toFixed(4)} GRIN</td>
                  </tr>
                </tbody>
              </Table>
            </Col>
          </Row>
        </Col>
      </Row>
    )
  }
}
