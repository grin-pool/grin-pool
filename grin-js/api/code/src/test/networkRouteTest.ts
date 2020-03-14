// process.env.NODE_ENV = 'test'

const chai = require('chai')
const chaiHttp = require('chai-http')
const should = chai.should()
const server = require('../app')

chai.use(chaiHttp)
//Our parent block
describe('networkRoutes return correct info', () => {
  describe('/GET block data', () => {
    it('/grin/block should return latest block data', (done) => {
      chai.request(server)
        .get('/grin/block')
        .end((err, res) => {
            res.should.have.status(200)
            res.body.should.be.a('object')
            res.body.height.should.be.a('number')
            res.body.height.should.be.above(0)
            res.body.timestamp.should.be.a('number')
            res.body.timestamp.should.be.above(1500000000)            
          done()
        })
    })
    
    it('/grin/block/height should return accurate data', (done) => {
      chai.request(server)
        .get('/grin/block/200')
        .end((err, res) => {
            res.should.have.status(200)
            // console.log('/grin/block/200 response is: ', res.body)
            res.body.should.be.a('object')
            res.body.height.should.be.a('number')
            res.body.height.should.be.above(198)
            res.body.timestamp.should.be.a('number')
            res.body.timestamp.should.be.above(1500000000)
            res.body.hash.should.be.a('string')
            res.body.total_difficulty.should.be.a('number')
          done()
        })
    })
    
    it('/grin/blocks/height,range should return accurate range data', (done) => {
      chai.request(server)
        .get('/grin/blocks/200,2')
        .end((err, res) => {
            res.should.have.status(200)
            res.body.should.be.a('array')
            res.body[0].height.should.be.a('number')
            res.body[0].height.should.be.above(198)
            res.body[0].timestamp.should.be.a('number')
            res.body[0].timestamp.should.be.above(1500000000)
            res.body[0].hash.should.be.a('string')
            res.body[0].total_difficulty.should.be.a('number')
            res.body[1].height.should.be.a('number')
            res.body[1].height.should.be.above(198)
            res.body[1].timestamp.should.be.a('number')
            res.body[1].timestamp.should.be.above(1500000000)
            res.body[1].hash.should.be.a('string')
            res.body[1].total_difficulty.should.be.a('number')            
          done()
        })
    })    
  })

  describe('/GET network stats for range', () => {
    it('/grin/stats/height,range should return valid network data', (done) => {
      chai.request(server)
        .get('/grin/stats/2000,2/')
        .end((err, res) => {
            // console.log('res is: ', res.body, ' and err is: ', err)          
            res.should.have.status(200)
            res.body.should.be.a('array')
            res.body[0].height.should.be.eql(1999)
            res.body[0].gps.length.should.be.eql(2)
            res.body[0].timestamp.should.be.a('number')
            res.body[0].difficulty.should.be.a('number')
            res.body[1].height.should.be.eql(2000)
            res.body[1].gps.length.should.be.eql(2)
            res.body[1].timestamp.should.be.a('number')
            res.body[1].difficulty.should.be.a('number')            
            res.body.length.should.be.eql(2)
          done()
        })
    })
    
    
  })

  describe('/GET network stats for range', () => {
    it('/grin/stats/height should return valid network data', (done) => {
      chai.request(server)
        .get('/grin/stats/2000/')
        .end((err, res) => {
            // console.log('res is: ', res.body, ' and err is: ', err)          
            res.should.have.status(200)
            res.body.should.be.a('object')
            res.body.height.should.be.eql(2000)
            res.body.gps.length.should.be.eql(2)
            res.body.timestamp.should.be.a('number')
            res.body.difficulty.should.be.a('number')            
          done()
        })
    })
    
    
  })  
})