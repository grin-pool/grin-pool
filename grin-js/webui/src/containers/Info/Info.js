import React, { Component } from 'react'
import { Container, Row, Col, Card, CardBody, Table, Alert } from 'reactstrap'
import { NavLink } from 'react-router-dom'
import { FAQComponent } from '../FAQ/FAQ'
import { MinerConfigsComponent } from '../MinerConfigs/MinerConfigs.js'
import { TutorialsComponent } from '../Instructions/Instructions.js'
import { C29_COLOR } from '../../custom/custom.js'
import ReactGA from 'react-ga'

export class InfoComponent extends Component {
  constructor (props) {
    super(props)
    ReactGA.initialize('UA-132063819-1')
    ReactGA.pageview(window.location.pathname + window.location.search)
  }

  render () {
    return (
      <Container className='dashboard'>
        <Alert className={'primary'} color='primary' style={{ fontSize: '1.1rem', textAlign: 'center', position: 'relative' }}>
          <p style={{ color: '#004085' }}>The following are the stratum server for connection to GrinPool:</p>
          <Table size='sm' hover style={{ marginBottom: '0px' }}>
            <thead>
              <tr>
                <th>Region</th>
                <th>Difficulty</th>
                <th>SSL</th>
                <th>Address : Port</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>USA</td>
                <td>4</td>
                <td>No</td>
                <td>stratum.grinpool.com:3333</td>
              </tr>
            </tbody>
          </Table>
        </Alert>
        <Row>
          <Col xs={12} md={12} lg={12} xl={12}>
            <h3 className='page-title'>Info</h3>
          </Col>
        </Row>
        <Row>
          <Col xs={12} md={12} lg={6} xl={6}>
            <Card>
              <CardBody id='aboutPage'>
                <h4 className='bold-text'>About GrinPool</h4><br />
                <p>How to mine in this pool:</p>
                <ul>
                  <li>Some About Text</li>
                </ul>
              </CardBody>
            </Card>
          </Col>
          <Col xs={12} md={12} lg={6} xl={6}>
            <Card>
              <CardBody>
                <h4>Important Info:</h4><br />
                <Table size='lg' responsive hover>
                  <tbody>
                    <tr>
                      <td>Stratum Server (SSL)</td>
                      <td>stratum.grinpool.com:3334</td>
                    </tr>
                  </tbody>
                </Table>
              </CardBody>
            </Card>
          </Col>
        </Row>
        <TutorialsComponent />
        <MinerConfigsComponent />
        <div>
          <Row>
            <Col xs={12} md={12} lg={12} xl={12}>
              <h3 className='page-title' id='workerRigConfig'>Worker + Rig Configurations</h3>
            </Col>
          </Row>
          <Row>
            <Col xs={12} md={12} lg={12} xl={12}>
              <Card>
                <CardBody>
                  <p style={{ marginLeft: '12px', fontSize: '16px' }}>In order to assign multiple rigs and workers to your GrinPool account, please configure your miner to set your username with the following format: <span style={{ fontFamily: 'monospace', color: C29_COLOR }}>myUsername.myRig.myWorker</span> where "myUsername" is your GrinPool username, "myRig" is the name of your rig, and "myWorker" is the name of your (optional) worker. Please note that the three fields are separated by periods. To access the individuals stats for each rig / worker, click on the "Rig Stats" link in the sidebar of the GrinPool website.</p>
                  <br />
                  <p>stratum_server_login = "captaincrypto.captainslair.rig1"</p>
                  <p>A breakdown showing individual graphs and statistics will be available by selecting the worker and rig from the dropdown on the <NavLink to='/rigs'>Rig Stats page</NavLink>.</p><br />
                  <img src='/img/worker-stats.png' style={{ maxHeight: '300px', maxWidth: '300px' }} /><br />
                  <p style={{ marginLeft: '12px', fontSize: '16px' }}>With this configuration all block rewards earned by any worker and / or rig under the given username will be credited to that user's account.</p>
                  <iframe width="560" height="315" src="https://www.youtube.com/embed/2bfrbKzwybg" frameBorder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
                </CardBody>
              </Card>
            </Col>
          </Row>
        </div>
        <FAQComponent />
      </Container>
    )
  }
}
