import React, { Component } from 'react'
import { Col, Card, CardBody, Alert } from 'reactstrap'
import ReactGA from 'react-ga'

export class AboutComponent extends Component {
  constructor (props) {
    super(props)
    ReactGA.initialize('UA-132063819-1')
    ReactGA.pageview(window.location.pathname + window.location.search)
  }

  render () {
    return (
      <Col>
        <Card>
          <CardBody>
            <div className='card__title'>
              <h5 className='bold-text'>Open-Source Mining Pool for the MimbleWimble Grin Blockchain</h5>
            </div>
            <h4 className='bold-text'>About GrinPool</h4>
            <p style={{ fontWeight: 'bold' }}>GRIN is currently mining on Testnet-4, with MainNet expected to launch soon™</p>
            <Alert color='danger' style={{ width: '50%', textAlign: 'center' }}>Please be warned that Testnet GRIN coins have no significant value.</Alert>
            <h4>How to mine in this pool:</h4>
            <ul>
              <li>Supports Linux and Windows miners: mimblewimble/grin-miner and mozkomor/GrinGoldMiner</li>
              <li>Configure your miner to connect to: stratum.mwgrinpool.com:3333</li>
              <li>Use your GRIN wallet URL as your stratum login, no password necessary</li>
              <li>Point your browser at <a href='http://MWGrinPool.com'>MWGrinPool.com</a></li>
              <li>Start your miner and watch your wallet fill with GRIN</li>
            </ul>
          </CardBody>
        </Card>
      </Col>
    )
  }
}
