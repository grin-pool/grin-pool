const poolRouter = require('express').Router()
import {
  mergeBlocks,
  filterFields,
  limitRange,
  getNewPasswordHashFromFullPassword,
  createHashedPassword,
  sanitizeHeight,
  getLatestPoolBlockHeight,
  getLatestNetworkBlockHeight,
  checkAuth
} from '../utils'
const fetch = require('node-fetch')
import jwt from 'jsonwebtoken'
const index = require('../index')
import { knex } from '../index'
const pbkdf2 = require('pbkdf2')
const crypto = require('crypto')
const basicAuth = require('express-basic-auth')
const express = require('express')
const app = express()
const multer = require('multer')
const upload = multer()
const getLegacyPassword = require('../verifyLegacyPassword')
const cors = require('cors')
import config from 'config'
import { FindUserResult, DatabasePoolBlock, DatabasePoolStat } from '../types/types'

const jwtSecretKey = config.get('jwtSecretKey')

// gets latest pool block, cache verified
poolRouter.get('/block', async (req, res, next) => {
  try {
    const latestPoolBlockHeight = await getLatestPoolBlockHeight()
    const results: DatabasePoolBlock[] = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
      .from('pool_blocks')
      .where('height', '=', latestPoolBlockHeight)
      .limit(1)
    index.cache.set(res.locals.cacheKey, JSON.stringify(results[0]), 'EX', 30)
    res.json(...results)
  } catch (e) {
    next(e)
  }
})

// cache verified
poolRouter.get('/blocks/:height,:range', sanitizeHeight, limitRange, async (req, res, next) => {
  try {
    // console.log('inside /blocks/:height,:range?')
    const range = res.locals.range
    // console.log('req.params is: ', req.params, ' and res.locals is: ', res.locals)
    let height = (res.locals && res.locals.height) || req.params.height
    height = parseInt(height)
    const rangeSyntax = ` LIMIT ${range}`
    const results: DatabasePoolBlock[] = await knex('pool_blocks')
      .select('height', 'hash', 'nonce', 'actual_difficulty', 'net_difficulty', 'state', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp'))
      .where('height', '<=', height)
      .orderBy('height', 'desc')
      .limit(range)
      index.cache.set(res.locals.cacheKey, JSON.stringify(results), 'EX', 30)
      res.json(results)
  } catch (error) {
    next(error)
  }
})

// cache verified, gets network data for a range of blocks
poolRouter.get('/stats/:height,:range/:fields?', sanitizeHeight, limitRange, async (req, res, next) => {
  try {
    const { fields } = req.params
    const range = res.locals.range
    let height = (res.locals && res.locals.height) || req.params.height
    let actualHeight = parseInt(height) < 1 ? 1 : parseInt(height) // is the height less than 1? Then use 1
    let actualRange = (parseInt(range) > actualHeight) ? actualHeight : parseInt(range) // range too big? limit to max
    if (!actualHeight || !actualRange) throw { statusCode: 400, message: 'Invalid height or range field specified' }
    // but if max is zero then it should find max
    const min = actualHeight - actualRange
    const maxHeight = await getLatestNetworkBlockHeight()
    const finalHeight = actualHeight > maxHeight ? maxHeight : actualHeight
    const poolStatsResults: DatabasePoolStat[] = await knex.select(['*', knex.raw('UNIX_TIMESTAMP(timestamp) as timestamp')])
      .from('pool_stats')
      .join('gps', 'height', '=', 'pool_stats_id')
      .where('height', '>', min)
      .andWhere('height', '<=', finalHeight)
      // console.log('poolStatsResults are: ', poolStatsResults)
      const output = mergeBlocks(poolStatsResults)
      index.cache.set(res.locals.cacheKey, JSON.stringify(output), 'EX', 30)
      res.json(output)
  } catch (e) {
    next(e)
  }
})

// log in
poolRouter.get('/users', cors(), async (req, res, next) => {
  try {
    const auth = req.headers['authorization']
    const encodedString: string = auth.replace('Basic ', '')
    const decoded = new Buffer(encodedString, 'base64').toString()
    const [username, enteredPassword] = decoded.split(':')
    const findUserResults: FindUserResult[] = await knex.select().from('users').where('username', '=', username)
    if (findUserResults.length !== 1) throw {statusCode: 401, message: 'Find user error'}
    const db = findUserResults[0]
    if (db.extra1) { // if it has a newer password
      const hashedPassword = getNewPasswordHashFromFullPassword(db, enteredPassword)
      if (hashedPassword.fullHashedPassword !== db.extra1) throw { statusCode: 403, message: 'Invalid credentials'}
      jwt.sign({ id: db.id, username: db.username }, jwtSecretKey, { expiresIn: '1 day'}, (err, token: string) => {
        if (err) throw { statusCode: 500, message: 'Error signing data'}
        res.status(200).json({ token, id: db.id })
      })
    } else { // if there is no new password
      const dbPasswordHash = db.password_hash // password in database
      const splitPasswordHash = dbPasswordHash.split('$') // parse it
      const roundString = splitPasswordHash[2] // take the number of rounds
      const roundSplit = roundString.split('=') // parse it
      const saltString = splitPasswordHash[3] // grab salt
      const legacyHashedPassword: string = await getLegacyPassword(enteredPassword, saltString, roundSplit[1])
      if (legacyHashedPassword === splitPasswordHash[4]) {
        const newHashedPassword = await createHashedPassword(enteredPassword) // creates new version of password
        jwt.sign({ id: db.id, username: db.username }, jwtSecretKey, { expiresIn: '1 day'}, (err, token: string) => {
          if (err) throw { statusCode: 500, message: 'Problem signing data' }
          res.status(200).json({ token, id: db.id })
        })
      } else {
        throw { statusCode: 403, message: 'Invalid credentials'}
      }
    }
  } catch (e) {
    next(e)
  }
})

// create user
poolRouter.post('/users', upload.fields([]), async (req, res, next) => {
  try {
    const { password, username } = req.body
    const salt = crypto.randomBytes(16).toString('base64').replace(/\=/g,'')
    const rounds = 656000
    crypto.pbkdf2(password, salt, rounds, 64, 'sha512', async (err, derivedKey) => {
      try {
        if (err) {
          throw { statusCode: 500, message: 'Problem signing data'}
        }
        const hashedPassword = derivedKey.toString('base64').toString().replace(/\=/g,'')
        const fullHashedPassword = `$6$rounds=${rounds}$${salt}$${hashedPassword}`
        const findUserResults: {id: number}[] = await knex.select('id')
          .from('users')
          .where('username', '=', username)
        if (findUserResults.length > 0) throw { statusCode: 409, message:  'Conflict with existing account' }
        console.log('password: ', password, ' salt: ', salt, 'rounds: ', rounds)
        const legacyHashedPassword: string = await getLegacyPassword(password, salt.substring(0, 15), rounds)
        const fullLegacyHashedPassword = `$6$rounds=${rounds}$${salt.substring(0, 15)}$${legacyHashedPassword}`
        console.log('fullLegacyHashedPassword is: ', fullLegacyHashedPassword)
        const insertUserResults = await knex('users')
          .insert({ username, extra1: fullHashedPassword, password_hash: fullLegacyHashedPassword })
          // console.log('insertUserResults is: ', insertUserResults)
        if (insertUserResults.length === 1) res.json({ username, id: insertUserResults[0] })
      } catch (e) {
        next(e)
      }
    })
  } catch (e) {
    next(e)
  }
})

poolRouter.post('/payment/http/:id', upload.fields([]), checkAuth, async (req, res, next) => {
  try {
    // console.log('req is: ', req)
    const { url, id } = req.params
    const cleanedUrl = req.body.cleanedUrl
    // console.log('cleanedUrl is: ', cleanedUrl)
    fetch(`https://api.mwfloopool.com/pool/payment/http/${id}/${cleanedUrl}`, { method: 'POST' })
      .then(response => {
        // console.log('response is: ', response)
        response.text()
          .then(output => {
            // console.log('output is: ', output)
            res.json(output)
          })
          .catch(e2 => console.log('e2 is: ', e2))
      })
      .catch(e1 => console.log('e1 is: ', e1))
  } catch (e) {
    next(e)
  }
})

module.exports = poolRouter