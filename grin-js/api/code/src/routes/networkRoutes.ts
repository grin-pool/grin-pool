const networkRouter = require('express').Router()
// var cache = require('express-redis-cache')()
import {
  mergeBlocks,
  sanitizeHeight,
  getLatestNetworkBlockHeight,
  limitRange
} from '../utils'
import { DatabaseGrinBlock, DatabaseGrinStat } from '../types/types'
import regeneratorRuntime from 'regenerator-runtime'
const app = require('../index')
const colors = require('colors');
import { knex } from '../index'
colors.setTheme({
  silly: 'rainbow',
  input: 'grey',
  verbose: 'cyan',
  prompt: 'grey',
  info: 'green',
  data: 'grey',
  help: 'cyan',
  warn: 'yellow',
  debug: 'blue',
  error: 'red'
})

networkRouter.get('/test', async (req, res, next) => {
  console.log('/grin/test touched')
  res.json('success')
})

// caching correctly
networkRouter.get('/block', async (req, res, next) => {
  try {
    const latestBlockHeight = await getLatestNetworkBlockHeight()
    const latestBlockResults: DatabaseGrinBlock[] = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
      .from('blocks')
      .where('height', latestBlockHeight)
    app.cache.set(res.locals.cacheKey, JSON.stringify(latestBlockResults[0]), 'EX', 20)
    res.json(latestBlockResults[0])
  } catch (e) {
    next(e)
  }
})

// gets latest block, is this endpoint even being used?
networkRouter.get('/block/:height?/:fields?', sanitizeHeight, async (req, res, next) => {
  try {
    let blockResult: DatabaseGrinBlock
    if (req.params.height) {
      const inputHeight = parseInt(req.params.height)      
      blockResult = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
        .from('blocks')
        .where('height', inputHeight)
        .limit(1)
    } else {
      const latestBlockHeight = await getLatestNetworkBlockHeight()
      blockResult = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
        .from('blocks')
        .where('height', latestBlockHeight)
        .limit(1)
    }
    app.cache.set(res.locals.cacheKey, JSON.stringify(blockResult[0]), 'EX', 30)
    res.json(blockResult[0])
  } catch (e) {
    next(e)
  }
})


// cache verified
networkRouter.get('/blocks/:height,:range/:fields?', sanitizeHeight, limitRange, async (req, res, next) => {
  try {
    const { fields } = req.params
    const range = res.locals.range
    let height = (res.locals && res.locals.height) || req.params.height
    if (!height || !range) throw { statusCode: 400, message: 'No height or range field specified' }
    const max = parseInt(height)
    const rangeNumber = parseInt(range)
    const min = max - rangeNumber
    let blockRangeResults: DatabaseGrinBlock[]
    if (fields) {
      const fieldsList = fields.split(',')
      blockRangeResults = await knex.select([...fieldsList, knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
        .from('blocks').where('height', '>', min)
        .andWhere('height', '<=', max)
    } else {
      blockRangeResults = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
        .from('blocks')
        .where('height', '>', min)
        .andWhere('height', '<=', max)
    }
    app.cache.set(res.locals.cacheKey, JSON.stringify(blockRangeResults), 'EX', 30)      
    res.json(blockRangeResults)
  } catch (e) {
    next(e)
  }
})

// cache verified, gets network data for a range of blocks
networkRouter.get('/stats/:height,:range/:fields?', sanitizeHeight, limitRange, async (req, res, next) => {
  try {
    const { fields } = req.params
    const range = res.locals.range
    let height = (res.locals && res.locals.block && res.locals.block.height) || (res.locals && res.locals.height) || req.params.height    
    let actualHeight = parseInt(height)
    // console.log('/stats/:height,:range/:fields, actualHeight is: ', actualHeight, ' and range is: ', range)
    if (!actualHeight || !range) throw { statusCode: 400, message: 'Invalid height or range field specified' }
    // but if max is zero then it should find max
    const min = actualHeight - range
    // console.log('/stats/:height,:range/:fields min is: ', min)
    let maxHeight = await getLatestNetworkBlockHeight()
    const finalHeight = actualHeight > maxHeight ? maxHeight : actualHeight
    const networkStatsRangeResults: DatabaseGrinStat[] = await knex
      .select(['grin_stats.difficulty', 'gps.gps', 'gps.edge_bits', 'blocks.height', knex.raw('UNIX_TIMESTAMP(grin_stats.timestamp) as timestamp'), 'blocks.secondary_scaling'])
      .from('grin_stats')
      .join('gps', 'grin_stats.height', '=', 'grin_stats_id')
      .join('blocks', 'grin_stats.height', '=', 'blocks.height')
      .where('grin_stats.height', '>', min)
      .andWhere('grin_stats.height', '<=', finalHeight)
    // console.log('/grin/stats/height,range/fields results are: ', networkStatsRangeResults)
    const output = mergeBlocks(networkStatsRangeResults)
    app.cache.set(res.locals.cacheKey, JSON.stringify(output), 'EX', 1)  
    res.json(output)
  } catch (e) {
    next(e)
  }
})


// cache verified, gets network data for a range of blocks
networkRouter.get('/stats/:height/:fields?', sanitizeHeight, async (req, res, next) => {
  try {
    const { fields } = req.params
    let height = (res.locals && res.locals.height) || req.params.height
    const actualHeight = parseInt(height)    
    if (actualHeight < 0 || !actualHeight) throw { statusCode: 400, message: 'Invalid block height specified' }
    // console.log('inside /stats/:height/:fields?')
    const networkStatResult: DatabaseGrinStat[] = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
      .from('grin_stats')
      .join('gps', 'height', 'grin_stats_id')
      .where('height', '=', actualHeight)
    const output = mergeBlocks(networkStatResult)
    app.cache.set(res.locals.cacheKey, JSON.stringify(output[0]), 'EX', 30)
    res.json(...output)
  } catch (e) {
    next(e)
  }
})

module.exports = networkRouter