const express = require('express')
const app = express()
const bodyParser = require('body-parser')
import jwt from 'jsonwebtoken'
const networkRouter = require('./routes/networkRoutes')
const poolRouter = require('./routes/poolRoutes')
const workerRouter = require('./routes/workerRoutes')
const cors = require('cors')
const config = require('config')
const morgan = require('morgan')
import { ServerError } from './types'
const bluebird = require('bluebird')
const redis = require("redis")
const redisDomain = (process.env.NODE_ENV === 'production') ? 'redis-master' : config.get('redisDomain')
export const cache = redis.createClient({
  host: redisDomain
})
const { promisify } = require('util')
export const rigCache = redis.createClient({
  host: 'redis-master'
})
export const getAsync = promisify(rigCache.get).bind(rigCache)
const colors = require('colors');

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

console.log(colors.help('node environment is: ', process.env.NODE_ENV))
console.log('config.redisCacheExpire is: ', config.get('redisCacheExpire'))
//console.log('index cache is: ', cache)
//console.log = () => {}

const PORT = 3009
const mySqlHost = (process.env.NODE_ENV === 'production') ? 'mysql' : 'localhost:3006'
const mySqlPassword = (process.env.NODE_ENV === 'production') ? process.env.MYSQL_ROOT_PASSWORD : 'root'
console.log('mySqlHost is: ', mySqlHost)
console.log('mySqlPassword is: ', mySqlPassword)

export const knex = require('knex')({
  client: 'mysql',
  connection: {
    host : mySqlHost,
    user : 'root',
    password : mySqlPassword,
    database : 'pool'
  },
  pool: {
    min: 0,
    max: 40
  }
})

knex.on('query-error', (error, obj) => {
  console.error('query-error: ', error)
  error.message = 'Database error'
})

app.use(cors())

if(config.util.getEnv('NODE_ENV') !== 'test' && config.util.getEnv('NODE_ENV') !== 'production') {
    // use morgan to log at command line
    app.use(morgan(':date[iso] :method :url :status :response-time ms - :res[content-length]')) //'combined' outputs the Apache style LOGs
}

app.listen(PORT, () => {
  console.log('listening on port ' + PORT)
  var date = new Date()
  var current_hour = date.getHours()
  console.log('Time is: ', date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds())
})

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*")
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization");
  next();
})

app.use((req, res, next) => {
  // console.log('req.url is: ', req.url)
  if (req.method === 'GET') {
    const cacheKey = `router_${req.url}`
    cache.get(cacheKey, async (error, value) => {
      if(error) console.log('cacheError is: ', error)
      if (value) {
        const parsedValue = JSON.parse(value)
        // console.log('returning cache')
        res.json(parsedValue)
      } else {
        // console.log('no cache value')
        res.locals.cacheKey = cacheKey
        // console.log('res.locals.cacheKey is now: ', res.locals.cacheKey )
        next()
      }
    })
  } else {
    next()
  }
})

app.use('/worker', (req, res, next) => {
  const bearerHeader = req.headers.authorization
  const authorization = req.headers['authorization']
  if (typeof bearerHeader !== 'undefined') {
    const bearer = bearerHeader.split(' ')
    const bearerToken = bearer[1]
    req.token = bearerToken
    next()
  } else {
    res.status(403).send('No authorization')
  }
})

app.use('/pool/payment/http', (req, res, next) => {
  const bearerHeader = req.headers.authorization
  const authorization = req.headers['authorization']
  if (typeof bearerHeader !== 'undefined') {
    const bearer = bearerHeader.split(' ')
    const bearerToken = bearer[1]
    req.token = bearerToken
    next()
  } else {
    res.status(403).send('No authorization')
  }
})

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true}))

// just list all routers
app.use('/grin', networkRouter)
app.use('/pool', poolRouter)
app.use('/worker', workerRouter)
app.use('/public', express.static(__dirname + '/public'))

app.get('*', function(req, res, next) {
  const err: ServerError = new Error('Page Not Found')
  err.statusCode = 404
  next(err);
})

// error-handling
app.use(function(err, req, res, next) {
  console.log('in error handler, err is: ', err)
  if (!err.statusCode) err.statusCode = 500 // If err has no specified error code, set error code to 'Internal Server Error (500)'
  //res.status(err.status || 500)

  console.error('err.statusCode is: ', err.statusCode, ' and err.message: ', err.message)
  console.error(err.stack)
  res.status(err.statusCode).send({message: err.message}) // All HTTP requests must have a response, so let's send back an error with its status code and message
})

app.on('uncaughtException', (err) => {
  console.log('Uncaught exception: ', JSON.stringify(err))
})

cache.on('message', (message) => {
  console.log('cache message: ', message)
})

cache.on("error", (err) => {
    console.log("Cache error " + err)
})

module.exports = app
