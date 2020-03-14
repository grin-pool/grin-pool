// process.env.NODE_ENV = 'test'

const chai = require('chai')
const chaiHttp = require('chai-http')
const exclude = require('chai-exclude')
const should = chai.should()
const server = require('../app')
const assert = chai.assert
const getLegacyPassword = require('../verifyLegacyPassword')

chai.use(chaiHttp)
chai.use(exclude)

//Our parent block
describe('hashPasswordLegacy returns accurate hash', () => {
  it('foo16:bar returns accurate legacy hash', async () => {
    const hash = await getLegacyPassword('bar', 'x3izv7./8HehO/bX', 656000)
    hash.should.be.eql('DqCWeJAlPlEaUiRh0kXYExoEQAXO6VVj.k98WDpSepj7z3M7d6.xpB0uVHq1Rc2gagRF8jTVDV9KFAHG50qoG0')
  })
})