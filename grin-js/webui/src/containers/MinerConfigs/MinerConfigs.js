import React, { Component } from 'react'
import { Row, Col, Card, CardBody, Collapse } from 'reactstrap'
const ReactMarkdown = require('react-markdown')

export class MinerConfigsComponent extends Component {
  constructor (props) {
    super(props)
    const renderedConfigs = configs.map((item) => {
      return (<CollapseConfig key={item.program} program={item.program} config={item.config} />)
    })
    this.state = {
      renderedConfigs
    }
  }

  render () {
    const { renderedConfigs } = this.state
    return (
      <div>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Miner Configurations</h3>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <Card>
              <CardBody id='minerConfigPage'>
                {renderedConfigs}
              </CardBody>
            </Card>
          </Col>
        </Row>
      </div>
    )
  }
}

export class CollapseConfig extends Component {
  constructor (props) {
    super(props)
    this.state = {
      open: true
    }
  }

  toggle = () => {
    const { isOpen } = this.state
    this.setState({
      isOpen: !isOpen
    })
  }

  render () {
    const { program, config } = this.props
    const { isOpen } = this.state
    return (
      <div>
        <h4 onClick={this.toggle} style={{ cursor: 'pointer', marginBottom: '22px' }}><strong>{program}</strong> Example:</h4>
        <Collapse isOpen={isOpen}>
          <Card>
            <CardBody>
              <ReactMarkdown source={config} />
            </CardBody>
          </Card>
        </Collapse>
      </div>
    )
  }
}

const configs = [
  {
    program: 'grin-miner (SSL)',
    config: '...\n\n&#35; listening grin stratum server url\n\nstratum_server_addr = "stratum.grinpool.com:3401"\n\n&#35; login for the stratum server (if required)\n\nstratum_server_login = "myUsername"\n\n&#35; password for the stratum server (if required)\n\nstratum_server_password = "MyPoolPassword"\n\n&#35; whether tls is enabled for the stratum server\n\nstratum_server_tls_enabled = true\n\n...'
  },
  {
    program: 'grin-miner (non-SSL)',
    config: '...\n\n&#35; listening grin stratum server url\n\nstratum_server_addr = "stratum.grinpool.com:3301"\n\n&#35; login for the stratum server (if required)\n\nstratum_server_login = "myUsername"\n\n&#35; password for the stratum server (if required)\n\nstratum_server_password = "MyPoolPassword"\n\n&#35; whether tls is enabled for the stratum server\n\nstratum_server_tls_enabled = false\n\n...'
  },
  {
    program: 'bminer (Windows + SSL)',
    config: '...\n\nSET ADDRESS=myUsername\n\nSET USERNAME=%ADDRESS%\n\nSET POOL=stratum.grinpoolcom:33334\n\nSET SCHEME=cuckaroo29+ssl\n\nSET PWD=myPassword\n\n...'
  },
  {
    program: 'bminer (Windows + non-SSL)',
    config: '...\n\nSET ADDRESS=myUsername\n\nSET USERNAME=%ADDRESS%\n\nSET POOL=stratum.grinpoolcom:33333\n\nSET SCHEME=cuckaroo29\n\nSET PWD=myPassword\n\n...'
  }
]
