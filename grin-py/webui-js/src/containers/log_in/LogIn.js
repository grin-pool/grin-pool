import React, { PureComponent } from 'react'

export default class LogIn extends PureComponent {
  constructor (props) {
    super(props)
    this.onClick = () => {

    }
  }

  render () {
    return <button onClick={this.onClick}>Log in</button>
  }
}

// if you want to add select, date-picker and time-picker in your app you need to uncomment the first
// four lines in /scss/components/form.scss to add styles
