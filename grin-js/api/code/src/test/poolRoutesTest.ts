// process.env.NODE_ENV = 'test'

const chai = require('chai')
const chaiHttp = require('chai-http')
const exclude = require('chai-exclude')
const should = chai.should()
const server = require('../app')
const crypto = require('crypto')

const assert = chai.assert
chai.use(chaiHttp)
chai.use(exclude)
//Our parent block
describe('poolRoutes return correct info', () => {
  describe('/GET block data', () => {
    it('/pool/block should return most recent pool block data', (done) => {
      chai.request(server)
        .get('/pool/block')
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
  })

  describe('/GET block data', () => {
    it('/pool/blocks/height,range should return range of recent pool blocks', (done) => {
      chai.request(server)
        .get('/pool/blocks/2000,2')
        .end((err, res) => {
            res.should.have.status(200)
            res.body.should.be.a('array')
            res.body[0].height.should.be.a('number')
            res.body[0].height.should.be.above(0)
            res.body[0].height.should.be.below(2001)
            res.body[0].timestamp.should.be.a('number')
            res.body[0].timestamp.should.be.above(1500000000)
            res.body[1].height.should.be.a('number')
            res.body[1].height.should.be.above(0)
            res.body[1].timestamp.should.be.a('number')
            res.body[1].timestamp.should.be.above(1500000000)
            res.body[1].height.should.be.below(2001)            
            res.body.length.should.be.eql(2)
          done()
        })
    })
  })

  describe('/GET block data', () => {
    it('/pool/stats/height,range should return range of pool stats', (done) => {
      chai.request(server)
        .get('/pool/stats/2000,2')
        .end((err, res) => {
            res.should.have.status(200)
            res.body.should.be.a('array')
            assert.deepEqualExcluding(res.body[0], {
                  'shares_processed': 2271,
                  'timestamp': 1547701885,
                  'dirty': false,
                  "id": 69309,
                  'total_blocks_found': 9,
                  'height': 1999,
                  'active_miners': 104,
                  'gps': [{'edge_bits': 29,'gps': 1752.73},{'edge_bits': 31,'gps': 0.752774}],
                  'total_shares_processed': 2221580,
                  "grin_stats_id": null,
                  "pool_stats_id": 1999,
                  "worker_stats_id": null,                  
              }, ['timestamp', 'dirty'])
            assert.deepEqualExcluding(res.body[1], {
                  'shares_processed': 352,
                  'timestamp': 1547701974,
                  'dirty': false,
                  "id": 69323,                  
                  'total_blocks_found': 9,
                  'height': 2000,
                  'active_miners': 104,
                  'gps': [{'edge_bits': 29,'gps': 1786.12},{'edge_bits': 31,'gps': 0.770642}],
                  'total_shares_processed': 2221932,
                  "grin_stats_id": null,
                  "pool_stats_id": 2000,
                  "worker_stats_id": null,                  
              }, ['timestamp', 'dirty'])
          done()
        })
    })
  })

  describe('/GET login data', () => {
    it('/pool/users login for valid user should return id and token', (done) => {
      chai.request(server)
        .get('/pool/users')
        .set('Authorization', 'Basic Zm9vMTY6YmFy') // data for foo16:bar
        .end((err, res) => {
            res.should.have.status(200)
            res.body.should.be.a('object')
            res.body.id.should.be.eql(175)
            res.body.token.should.be.a('string')
          done()
        })
    })

    it('/pool/users login for unregistered user should return a 401', (done) => {
      chai.request(server)
        .get('/pool/users')
        .set('Authorization', 'Basic YWZvbzE2OmJhcmFzZGY=') // data for foo16:bar
        .end((err, res) => {
            res.should.have.status(401)
            // console.log('res.text is: ', res.text)            
            res.body.should.be.eql({ message: 'Find user error' })
          done()
        })
    })

    it('/pool/users login for valid user (with new password) should return id and token', (done) => {
      chai.request(server)
        .get('/pool/users')
        .set('Authorization', 'Basic bW9jaGE6dGVzdA==') // data for mocha:test
        .end((err, res) => {
            res.should.have.status(200)
            res.body.should.be.a('object')
            res.body.id.should.be.eql(4953)
            res.body.token.should.be.a('string')
          done()
        })
    })

    it('/pool/users login for registered user with new password but wrong input password should return a 403', (done) => {
      chai.request(server)
        .get('/pool/users')
        .set('Authorization', 'Basic bW9jaGE6ZmFrZQ==') // data for mocha:fake
        .end((err, res) => {
            res.should.have.status(403)
            // console.log('res.text is: ', res.text)            
            res.body.should.be.eql({ message : 'Invalid credentials' })
          done()
        })
    })    
  })

  describe('/POST user account creation', () => {
    it('/pool/users lets us create a random new user', (done) => {
      const username = `mwtest-${crypto.randomBytes(20).toString('hex')}`
      const password = crypto.randomBytes(20).toString('hex')
      chai.request(server)
        .post('/pool/users')
        .send({ username, password }) // data for mocha:fake
        .end((err, res) => {
            console.log('res is: ', res)
            res.should.have.status(200)
            res.body.id.should.be.a('number')
            res.body.username.should.be.eql(username)
          done()
        })
    })
  })

  it('/pool/users gives us errror when producing a duplicate username', (done) => {
    const username = 'foo16'
    const password = crypto.randomBytes(20).toString('hex')
    chai.request(server)
      .post('/pool/users')
      .send({ username, password }) // data for mocha:fake
      .end((err, res) => {
          res.should.have.status(409)
          // console.log('res.text is: ', res.text)
          res.body.should.be.eql({ message: 'Conflict with existing account' })
        done()
      })
  })
})