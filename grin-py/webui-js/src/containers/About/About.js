import React, { Component } from 'react'
import { Col, Card, CardBody, Alert } from 'reactstrap'

export class AboutComponent extends Component {
  render () {
    return (
      <Col>
        <Card>
          <CardBody>
            <div className='card__title'>
              <h5 className='bold-text'>Open-Source Mining Pool for the MimbleWimble Grin Blockchain</h5>
            </div>
            <h4 className='bold-text'>About MWGrinPool</h4>
            <p style={{ fontWeight: 'bold' }}>GRIN is currently mining on FlooNet, with MainNet expected to launch January 15th 2019</p>
            <Alert color='danger' style={{ width: '50%', textAlign: 'center' }}>Please be warned that FlooNet GRIN coins have no significant value.</Alert>
            <h4>How to mine in this pool:</h4>
            <ul>
              <li>Supports Linux and Windows miners: mimblewimble/grin-miner and mozkomor/GrinGoldMiner</li>
              <li><a href="https://medium.com/@blade.doyle/cpu-mining-on-mwgrinpool-com-how-to-efb9ed102bc9">CPU Mining Guide</a></li>
              <li><a href="https://medium.com/@blade.doyle/gpu-mining-on-mwgrinpool-com-how-to-72970e550a27">GPU Mining Guide</a></li>
              <li><a href="https://medium.com/@blade.doyle/configure-payments-on-mwgrinpool-com-how-to-7b84163ec467">Payment Configuration Guide</a></li>
              <li><a href="https://gitter.im/grin-pool/Lobby">Gtter Discussion Channel</a></li>
            </ul>
          </CardBody>
        </Card>
      </Col>
    )
  }
}
