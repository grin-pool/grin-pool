const mysql = require('mysql')
const pbkdf2 = require('pbkdf2')
const crypto = require('crypto')
const index = require('./index')
const jwt = require('jsonwebtoken')
const config = require('config')
import { FindUserResult, BlockGpsStat, MergedBlockGpsStat, MergeBlocksInput, WorkerShareStat, PoolStat, DatabaseGrinStat } from './types/types'
const util = require('util')
import { knex } from './index'
export const numberRounds = 656000
const jwtSecretKey = config.get('jwtSecretKey')
const maxBlockRange = config.get('maxBlockRange')

export const checkAuth = (req, res, next) => {
  // console.log('inside checkAuth, req.token is: ', req.token)
  try {
    // console.log('req.token is: ', req.token)
    const decoded: { id: number, username: string, iat: number, exp: number } = jwt.verify(req.token, jwtSecretKey)
    // console.log('checkAuth decoded is: ', decoded)
    req.userData = decoded
    if (decoded.id !== parseInt(req.params.id)) {
      // console.log('ids do not match')
      res.json({ message: 'Cannot access that user data' }).end()
      return
    }
    next()
  } catch (e) {
    console.log('checkAuth rejects: ', e)
    return res.status(401).json({ message: e })
  }
}

export const mergeBlocks = (results: MergeBlocksInput[] ): MergedBlockGpsStat[] => {
  // console.log('a mergeBlocks result: ', results)
  const output = []
  results.forEach((resultsRow) => {
    const index = output.findIndex(outputRow => outputRow.height === resultsRow.height)
    // if it's a new row for the block
    if (index === -1) {
      const gps = [
          {
            edge_bits: resultsRow.edge_bits,
            gps: resultsRow.gps
          }
        ]
      delete resultsRow.edge_bits
      output.push({
        ...resultsRow,
        gps
      })
    } else {
      output[index].gps.push({
        edge_bits: resultsRow.edge_bits,
        gps: resultsRow.gps
      })
    }
  })
  // console.log('a mergeBlock output is: ', output[0])
  return output
}

export const filterFields = (fields: string, results: Object[]): Object[] => {
  const fieldsList = fields.split(',')
  if (fieldsList.length > 0) {
    const filteredResults = results.map((item) => {
      let filteredItem = {}
      fieldsList.forEach(field => {
        filteredItem[field] = item[field]
      })
      return filteredItem
    })
    return filteredResults
  }
}

// get the new format for the password hash based on the user row and entered password (result may not match db.extra1)
export const getNewPasswordHashFromFullPassword = (
  userRow: FindUserResult, enteredPassword: string
): { modifiedPassword: string, fullHashedPassword: string} => {
  const fullPassword = userRow.extra1 // grab the extra1 field
  const salt = fullPassword.split('$')[3] // grab the salt portion
  const derivedKey = crypto.pbkdf2Sync(enteredPassword, salt, numberRounds, 64, 'sha512') // derive the key from entered password
  const modifiedPassword = derivedKey.toString('base64').toString().replace(/\=/g,'') // entered password hash put in acceptable format
  const fullHashedPassword = `$6$rounds=${numberRounds}$${salt}$${modifiedPassword}` // final form from entered password
  return ({ modifiedPassword, fullHashedPassword }) // return both formats
}

// creation of new password hash with new format, based on an entered password
export const createHashedPassword = (enteredPassword: string): Promise<{ modifiedPassword: string, fullHashedPassword: string }> => {
  return new Promise((resolve, reject) => {
    try {
      const salt = crypto.randomBytes(16).toString('base64').replace(/\=/g,'')
      const derivedKey = crypto.pbkdf2Sync(enteredPassword, salt, numberRounds, 64, 'sha512') // derive the key
      const modifiedPassword = derivedKey.toString('base64').replace(/\=/g,'') // put in acceptable format
      const fullHashedPassword = `$6$rounds=${numberRounds}$${salt}$${modifiedPassword}` // final form
      resolve({ modifiedPassword, fullHashedPassword })
    } catch (e) {
      reject({ statusCode: 500, message: 'Password hashing error'})
    }
  })
}

export const aggregateShareCreditsFromUserStats = (sharesRows): { c29: number, c31: number} => {
  // console.log('sharesRows item: ', sharesRows[0])
  const credit = {
    c29: 0,
    c31: 0
  }
  sharesRows.forEach((row) => {
    if (row.edge_bits === 29) {
      const maximum = Math.max(29, row.secondary_scaling)
      credit.c29 = credit.c29 + (row.valid * maximum)
    } else if (row.edge_bits === 31) {
      const weight = Math.pow(2, (1 + row.edge_bits - 24)) * row.edge_bits
      credit.c31 = credit.c31 + (row.valid * weight)
    }
  })
  return credit
}


export const aggregateShareCreditsFromPoolShares = (
  sharesRows: Array<{ secondary_scaling: number, share_counts: null | string }>
): { c29: number, c31: number } => {
  // console.log('aggregateShareCreditsFromPoolShares item is: ', aggregateShareCreditsFromPoolShares[0])
  const credit = {
    c29: 0,
    c31: 0
  }
  sharesRows.forEach((row) => {
    if (row.share_counts) {
      const parsedShareCounts: { C29?: any, C31?: any } = JSON.parse(row.share_counts)
      if (parsedShareCounts.C29) {
        const maximum = Math.max(29, row.secondary_scaling)
        credit.c29 = credit.c29 + (parsedShareCounts.C29.valid * maximum)
      }
      if (parsedShareCounts.C31) {
        const weight = Math.pow(2, (1 + 31 - 24)) * 31
        credit.c31 = credit.c31 + (parsedShareCounts.C31.valid * weight)
      }
    }
  })
  // console.log('aggregateShareCreditsFromPoolShares credit is: ', credit)
  return credit
}

export const calculateCreditFromPoolStat = (row): number => {
  let credit = {
    c29: 0,
    c31: 0
  }
  // console.log('row is: ', row)
  if (row.share_counts) {
    const shareCounts = JSON.parse(row.share_counts)
    if (shareCounts.C29) {
      const maximum = Math.max(29, row.secondary_scaling)
      credit.c29 = credit.c29 + (shareCounts.C29.valid * maximum)
    }
    if (shareCounts.C31) {
      const weight = Math.pow(2, (1 + 31 - 24)) * 31
      credit.c31 = credit.c31 + (shareCounts.C31.valid * weight)
    }
  }
  return credit.c29 + credit.c31
}


export const calculateBlockReward = (height: number, workerStats: WorkerShareStat[], poolStats: PoolStat[]) => {
  // console.log('height is: ', height)
  // console.log('workerStats: ', workerStats[0])
  // console.log('poolStats: ', poolStats[0])
  let aggregatedPoolCredit = 0
  let aggregatedUserCredit = 0
  poolStats.forEach(poolStat => {
    if (poolStat.height <= height && poolStat.height > height - 59) {
      aggregatedPoolCredit += calculateCreditFromPoolStat(poolStat)
    }
  })
  workerStats.forEach(workerStat => {
    if (workerStat.height <= height && workerStat.height > height - 59) {
      const additionalCredit = calculateCreditFromUserStat(workerStat, workerStat.height)
      aggregatedUserCredit += additionalCredit
      // console.log('in calculateBlockReward and workerStat height is: ', workerStat.height, ' and additional credit is: ', additionalCredit)
    }
  })
  if (aggregatedPoolCredit === 0) return 0
  // console.log('height: ', height, ' aggregatedUserCredit: ', aggregatedUserCredit, ' aggregatedPoolCredit: ', aggregatedPoolCredit, 'portion: ', aggregatedUserCredit / aggregatedPoolCredit)
  const portion = aggregatedUserCredit / aggregatedPoolCredit
  const userReward =  grinToNanoGrin(60) * portion
  // console.log(height, ' userReward (block) is: ', userReward)
  return userReward
}

export const calculateCreditFromUserStat = (row: WorkerShareStat, height: number): number => {
  // console.log('calculatCreditFromUserStat row: ', row)
  const credit = {
    c29: 0,
    c31: 0
  }
  if (row.share_edge_bits === 29) {
    const maximum = Math.max(29, row.secondary_scaling)
    credit.c29 += (row.valid * maximum)
  } else if (row.share_edge_bits === 31) {
    const weight = Math.pow(2, (1 + row.share_edge_bits - 24)) * row.share_edge_bits
    credit.c31 += (row.valid * weight)
  }
  if (height === 104194)  console.log('height 104194, ', 'row: ', row)
  return credit.c29 + credit.c31
}

export const getLatestNetworkBlockHeight  = (): Promise<number> => {
  return new Promise((resolve, reject) => {
    try {
      index.cache.get('router_max_network_block_height', async (err, item: string) => {
        let maxBlockHeight
        if (err || !item) {
          const maxBlockHeightResult = await knex('blocks').max({ height: 'height'}).limit(1)
          maxBlockHeight = maxBlockHeightResult[0].height
          index.cache.set('router_max_network_block_height', maxBlockHeight, 'EX', 20)
        } else {
          maxBlockHeight = parseInt(item)
        }
        resolve(maxBlockHeight)
      })
    } catch (e) {
      throw { statusCode: 500, message: 'Error getting latest block height'}
    }
  })
}

export const getLatestPoolBlockHeight  = (): Promise<number> => {
  return new Promise((resolve, reject) => {
    try {
      index.cache.get('router_max_block_height', async (err, item) => {
        let maxBlockHeight
        if (err || !item) {
          const maxBlockHeightResult = await knex('pool_blocks').max({ height: 'height'}).limit(1)
          maxBlockHeight = maxBlockHeightResult[0].height
          index.cache.set('router_max_pool_block_height', maxBlockHeight, 'EX', 20)
        } else {
          maxBlockHeight = parseInt(item)
        }
        resolve(maxBlockHeight)
      })
    } catch (e) {
      throw { statusCode: 500, message: 'Error getting latest block height'}
    }
  })
}

export const limitRange = async (req, res, next) => {
  // console.log('limitRange starting off with req.params.range: ', req.params.range)
  const range: number = req.params.range
  const maxRange = maxBlockRange
  const defaultRange = maxBlockRange
  let reducedRange = defaultRange
  if (range) reducedRange = range
  if (range > maxRange) reducedRange = maxRange
  res.locals.range = range
  // console.log('limitRange result is: ', range)
  next()
}



export const sanitizeHeight = async (req, res, next) => {
  // console.log('inside sanitizeHeight')
  if (req.params && req.params.height && (parseInt(req.params.height) < 1)) {
    // console.log('inside sanitizing height conditional')
    index.cache.get(`router_/grin/block`, async (err, item: string) => {
      // console.log('inside sanitizeHeight cache.get, err is: ', err)
      if (err) throw { statusCode: 500, message: 'Could not retrieve max block height from cache'}
      if (item) {
        // console.log('inside sanitize height and found cached block')
        const blockData = JSON.parse(item)
        res.locals.block = blockData
        next()
      } else {
        const maxHeightResult = await knex('blocks').select({ maxHeight: 'height' }).limit(1)
        if (err) throw { statusCode: 500, message: 'Could not find max block height' }
        // console.log('maxHeightResult: ', maxHeightResult)
        const maxHeight = parseInt(maxHeightResult[0].maxHeight)
        res.locals.height = maxHeight
        index.cache.set(`router_/grin/block.height`, maxHeight, 'EX', 1)
        // console.log('res.locals is: ', res.locals)
        next()
      }
    })
  } else {
    next()
  }
}

export const nanoGrinToGrin = (nanoGrin: number): number => {
  return nanoGrin / 1000000000
}

export const grinToNanoGrin = (grin: number): number => {
  return grin * 1000000000
}