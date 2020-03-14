const workerRouter = require('express').Router()
const basicAuth = require('express-basic-auth')
import {
  mergeBlocks,
  filterFields,
  limitRange,
  checkAuth,
  aggregateShareCreditsFromPoolShares,
  aggregateShareCreditsFromUserStats,
  getLatestNetworkBlockHeight,
  sanitizeHeight,
  calculateBlockReward
} from '../utils'
const app = require('../index')
import { cache, knex, rigCache, getAsync } from '../index'
import {
  WorkerGpsStat,
  DatabaseWorkerStat,
  BlockAlgoValidShare,
  DatabasePoolUtxo,
  DatabasePoolPayment,
  DatabasePoolBlock,
  PoolSharesQueryResult,
  UserSharesQueryResult
} from '../types/types'

workerRouter.get('/stats/:id/:height,:range/:fields?', sanitizeHeight, limitRange, checkAuth, async (req, res, next) => {
  try {
    const { height, fields, id } = req.params
    const range = res.locals.range
    if (!height || !range) throw { statusCode: 400, message: 'No height or range field specified' }
    const max = parseInt(height)
    const rangeNumber = parseInt(range)
    const min = max - rangeNumber
    // console.log('min is: ', min, ' max is: ', max, ' and rangeNumber is: ', rangeNumber)
    const results: WorkerGpsStat[] = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
      .from('worker_stats')
      .join('gps', 'gps.worker_stats_id', '=', 'worker_stats.id')
      .where('worker_stats.height', '>', min)
      .andWhere('worker_stats.height', '<=', max)
      .andWhere('worker_stats.user_id', '=', id)
      .limit(range * 2)
    // console.log('/stats/:id/:height,:range/:fields? results.length: ', results.length)
    const output = mergeBlocks(results)
    // console.log('merged blocks output length is: ', output.length)
    res.json(output)
    app.cache.set(res.locals.cacheKey, JSON.stringify(output), 'EX', 20)
  } catch (e) {
    next(e)
  }
})

// get rig data for a user in a block range
workerRouter.get('/rigs/:id/:height,:range', sanitizeHeight, limitRange, checkAuth, async (req, res, next) => {
  try {
    const { height, fields, id } = req.params
    const range = res.locals.range
    if (!height || !range) throw { statusCode: 400, message: 'No height or range field specified' }
    const max = parseInt(height)
    const rangeNumber = parseInt(range)
    const min = max - rangeNumber
    let rigData = []
    let blockHeights = []
    // console.log('min is: ', min)
    for (let iterator = min; iterator <= max; iterator++) {
      const rigCacheKey = `rigdata.${iterator}.${id}`
      // rigData.push(getAsync(rigCacheKey))
      rigData[iterator] = getAsync(rigCacheKey)
      blockHeights.push(iterator)
      // console.log('iterator is: ', iterator)
    }
    // console.log('blockHeights is: ', blockHeights)
    const temp = await Promise.all(Object.values(rigData))
    // console.log('rigData is: ', rigData)

    const finalRigData = {}
    let index = 0
    // console.log('rigData is: ', rigData)
    temp.forEach((item) => {
      let parsedData = JSON.parse(item)
      if (parsedData) {
        // console.log('parsedData is: ', parsedData)
        finalRigData[blockHeights[index]] = parsedData
        // parsedData.height = blockHeights[index]
        // finalRigData.push(parsedData)
        // console.log('index is: ', index, ' an blockHeights[index] is: ', blockHeights[index])
      }
      index++
    })
    // console.log('barely inside of for loop and rigData is: ', finalRigData)
    res.json(finalRigData)
  } catch (e) {

  }
})

// complete
workerRouter.get('/stat/:id/:fields?', checkAuth, async (req, res, next) => {
  try {
    const { id, fields } = req.params
    const latestWorkerStatSubquery: { id: number }[] = knex('worker_stats')
      .max('id').
      where('user_id', '=', id)
      .limit(1)
    const latestWorkerStatResults: DatabaseWorkerStat[] = await knex.select()
      .from('worker_stats')
      .where('user_id', '=', id)
      .andWhere('id', '=', latestWorkerStatSubquery)
      .limit(1)
    let output = latestWorkerStatResults
    app.cache.set(res.locals.cacheKey, JSON.stringify(output[0]), 'EX', 20)
    res.json(...output)
  } catch (e) {
    next(e)
  }
})

// new
workerRouter.get('/shares/:id/:height,:range/:fields?', checkAuth, sanitizeHeight, limitRange, async (req, res, next) => {
  try {
    const { id, height } = req.params
    const range = res.locals.range
    if (!height || !range) throw { statusCode: 400, message: 'No height or range field specified' }
    const max = parseInt(height)
    const rangeNumber = parseInt(range)
    const min = max - rangeNumber
    // console.log('/shares/:id/:height,:range/:fields, rangeNumber is: ', rangeNumber, ' max is: ', max, ' and min is: ', min)
    const workerShareResults: BlockAlgoValidShare[] = await knex.select(['edge_bits', 'valid', 'worker_shares.height as height'])
      .from('shares')
      .join('worker_shares', 'shares.parent_id', '=', 'worker_shares.id')
      .where('worker_shares.height', '<=', max)
      .andWhere('worker_shares.height', '>', min)
      .andWhere('worker_shares.user_id', '=', id)
    // console.log('workerShareResults are: ', workerShareResults)
    app.cache.set(res.locals.cacheKey, JSON.stringify(workerShareResults), 'EX', 60 * 60)
    res.json(workerShareResults)
  } catch (e) {
    next(e)
  }
})

// checking
workerRouter.get('/utxo/:id', checkAuth, async (req, res, next) => {
  try {
    const { id } = req.params
    const results: DatabasePoolUtxo = await knex.select()
      .from('pool_utxo')
      .where('user_id', '=', id)
      .limit(1)
    delete results.id
    app.cache.set(res.locals.cacheKey, JSON.stringify(results[0]), 'EX', 60)
    res.json(results[0])
  } catch (e) {
    next(e)
  }
})

// complete
workerRouter.get('/payment/:id', checkAuth, async (req, res, next) => {
  try {
    const { id } = req.params
    const workerLatestPaymentSubquery: { timestamp: any }[] = await knex('pool_payment')
      .max('timestamp')
      .where('user_id', '=', id)
    const result: DatabasePoolPayment[] = await knex('pool_payment')
      .where('user_id', '=', id)
      .andWhere('timestamp', '=', workerLatestPaymentSubquery)
      // console.log('/payment/:id result is: ', result)
      app.cache.set(res.locals.cacheKey, JSON.stringify(result), 'EX', 60)
      res.json(result)
  } catch (e) {
    next(e)
  }
})

workerRouter.get('/payments/:id/:range', checkAuth, limitRange, async (req, res, next) => {
  try {
    // console.log('in /payments/:id/:range')
    const { id } = req.params
    const range = res.locals.range
    if (!range) throw { statusCode: 400, message: 'No block range set' }
    const results: DatabasePoolPayment[] = await knex.select()
      .from('pool_payment')
      .where('user_id', '=', id)
      .orderBy('timestamp', 'desc')
      .limit(range)
      app.cache.set(res.locals.cacheKey, JSON.stringify(results), 'EX', 60)
      res.json(results)
  } catch (e) {
    next(e)
  }
})

export const getUserEstimatedRewardForBlock =  (id: number, height: number, res, next) => {
  // console.log('inside getUserEstimatedRewardForBlock function')
  const getUserEstimatedRewardsForBlockCacheKey = `api_getUserEstimatedRewardForBlock_${id}_${height}`
  let getUserEstimatedRewardsForBlockResult
  return new Promise((resolve, reject) => {
    cache.get(getUserEstimatedRewardsForBlockCacheKey, async (error, getUserEstimatedRewardsCache: string) => {
      if (getUserEstimatedRewardsCache) {
        // console.log(getUserEstimatedRewardsForBlockCacheKey, ' already found: ', getUserEstimatedRewardsCache)
        resolve(parseInt(getUserEstimatedRewardsCache))
      } else {
        try {
          // console.log(getUserEstimatedRewardsForBlockCacheKey, ' not found')
          const creditRange = 60
          const escapedMinHeight = height - creditRange
          // get data for pool blocks in last day
          // const poolBlockMinedQuery = `SELECT * FROM pool_blocks WHERE state = 'new' AND height = ${height} LIMIT 1`
          const poolBlockMined: DatabasePoolBlock[] = await knex('pool_blocks')
            .where('state', '=', 'new')
            .andWhere('height', '=', height)
            .limit(1)
          // no blocks = no reward
          // console.log('poolBlocksMined are: ', poolBlockMined)
          if (poolBlockMined.length === 0) res.status(200).json(0)
          let poolSharesWeights
          let userSharesWeights
          const poolBlockShareWeightCacheKey = `api_pool_shares_weights_${height}`
          const userBlockShareWeightCacheKey = `api_user_shares_weights_${id}_${height}`
          //console.log('poolBlockShareWeightCacheKey is: ', poolBlockShareWeightCacheKey)
          cache.get(poolBlockShareWeightCacheKey, async (error, poolSharesCreditCache: string) => {
            if (error) throw {statusCode: 500, message: 'Error getting cache'}
            const poolSharesCredit: {c29: number, c31: number} = JSON.parse(poolSharesCreditCache)
            if (poolSharesCredit) {
              poolSharesWeights = poolSharesCredit
            } else {
              // need to get pool shares for 60-block range
              const poolSharesResults: PoolSharesQueryResult[] = await knex('pool_stats')
                .select()
                .join('blocks', 'pool_stats.height', 'blocks.height')
                .where('blocks.height', '<=', height)
                .andWhere('blocks.height', '>', escapedMinHeight)
              poolSharesWeights = aggregateShareCreditsFromPoolShares(poolSharesResults)
              cache.set(poolBlockShareWeightCacheKey, JSON.stringify(poolSharesWeights), 'EX', 60 * 60 * 24)
              cache.get(userBlockShareWeightCacheKey, async (error, userSharesCreditCache: string) => {
                if (error) throw { statusCode: 500, message: 'Error getting cache' }
                const userSharesCredit: { c29: number, c31: number } = JSON.parse(userSharesCreditCache)
                if (userSharesCredit) {
                  userSharesWeights = userSharesCredit
                } else {
                  const userSharesResults: UserSharesQueryResult[] = await knex('shares')
                    .select()
                    .join('worker_shares as ws', 'ws.id', 'shares.parent_id')
                    .join('blocks as b', 'b.height', 'ws.height')
                    .where('ws.user_id', '=', id)
                    .andWhere('ws.height', '<=', height)
                    .andWhere('ws.height', '>', escapedMinHeight)
                  userSharesWeights = aggregateShareCreditsFromUserStats(userSharesResults)
                  cache.set(userBlockShareWeightCacheKey, JSON.stringify(userSharesWeights), 'EX', 60 * 60 * 24)
                }
                //console.log('userSharesWeights is: ', userSharesWeights, ' and poolSharesWeights is: ', poolSharesWeights)
                const aggregatePoolSharesWeight = poolSharesWeights.c29 + poolSharesWeights.c31
                const aggregateUserSharesWeight = userSharesWeights.c29 + userSharesWeights.c31
                //console.log('aggregatePoolSharesWeight is: ', aggregatePoolSharesWeight, ' aggregateUserSharesWeight is: ', aggregateUserSharesWeight)
                if (aggregatePoolSharesWeight === 0 || aggregateUserSharesWeight === 0) {
                  resolve(0)
                  return
                }
                const blockRewardRate = aggregateUserSharesWeight / (aggregatePoolSharesWeight) // keep in mind that pool shares will include user's shares
                const blockReward = Math.floor(60000000000 * blockRewardRate) // sent in nanogrin
                // console.log('blockReward is: ', blockReward)
                cache.set(getUserEstimatedRewardsForBlockCacheKey, JSON.stringify(blockReward), 'EX', 60 * 60 * 24)
                resolve(blockReward)
              })
            }
          })
        } catch (e) {
          reject(e)
        }
      }
    })
  })
}

// complete, get payment estimate for a (immature) block
workerRouter.get('/estimate/payment/:id/:height', checkAuth, sanitizeHeight, async (req, res, next) => {
  try {
    const { height, id } = req.params
    if (!height) throw { statusCode: 400, message: 'No height field specified' }
    const reward = await getUserEstimatedRewardForBlock(id, height, res, next)
    app.cache.set(res.locals.cacheKey, reward, 'EX', 60 * 60)
    res.json(reward)
    return
  } catch (e) {
    next(e)
  }
})

// gets user's immature balances
workerRouter.get('/estimate/payment/:id', checkAuth, async (req, res, next) => {
  try {
    const { id } = req.params
    const poolBlocksMinedResults: DatabasePoolBlock[] = await knex('pool_blocks')
      .select('height')
      .where('state', '=', 'new')
      .orderBy('height', 'desc')
    //console.log('poolBlocksMinedResults is: ', poolBlocksMinedResults)
    if (poolBlocksMinedResults.length === 0) {
      res.status(200).json(0)
      return
    }
    const maxPoolBlockHeight = poolBlocksMinedResults[0].height
    const minBlockHeight = maxPoolBlockHeight - 1440 - 60
    const poolSharesQuery = knex('pool_stats')
      .select()
      .join('blocks', 'pool_stats.height', 'blocks.height')
      .where('blocks.height', '<=', maxPoolBlockHeight)
      .andWhere('blocks.height', '>', minBlockHeight)
    const userSharesQuery = knex('shares')
      .select('*', knex.raw('shares.edge_bits AS share_edge_bits'))
      .join('worker_shares as ws', 'ws.id', 'shares.parent_id')
      .join('blocks as b', 'b.height', 'ws.height')
      .where('ws.user_id', '=', id)
      .andWhere('ws.height', '<=', maxPoolBlockHeight)
      .andWhere('ws.height', '>', minBlockHeight)
    const [ poolSharesResults, userSharesResults ]: [PoolSharesQueryResult[], UserSharesQueryResult[]] = await Promise.all([poolSharesQuery, userSharesQuery])
    // console.log('poolSharesResults[0]: ', poolSharesResults[0])
    // console.log('userSharesResults[0]: ', userSharesResults[0])
    let rewards = 0
    poolBlocksMinedResults.forEach((result) => {
      const additionalReward = calculateBlockReward(result.height, userSharesResults, poolSharesResults)
      // console.log('additionalReward for height ', result.height, ' is: ', additionalReward / 1000000000)
      rewards += additionalReward
    })
    app.cache.set(res.locals.cacheKey, rewards, 'EX', 60 * 2)
    // console.log('rewards is: ', rewards / 1000000000)
    res.status(200).json(rewards)
  } catch (e) {
    next(e)
  }
})

module.exports = workerRouter