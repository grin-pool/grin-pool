import React, { PureComponent } from 'react'
import { Table } from 'reactstrap'
import PropTypes from 'prop-types'

export default class TableComponent extends PureComponent {
  static propTypes = {
    striped: PropTypes.bool,
    hover: PropTypes.bool,
    responsive: PropTypes.bool,
    className: PropTypes.string
  }

  render () {
    return (
      <Table className={this.props.className} striped={this.props.striped} hover={this.props.hover}
        responsive={this.props.responsive}>
        {this.props.children}
      </Table>
    )
  }
}
