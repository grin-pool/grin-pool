import React, { PureComponent } from 'react'
import TextField from '@material-ui/core/TextField'
import SearchIcon from 'mdi-react/SearchIcon'

export default class TopbarSearch extends PureComponent {
  constructor (props) {
    super(props)
    this.state = { inputOpen: false }
    this.onInputOpen = this.onInputOpen.bind(this)
  }

  onInputOpen (e) {
    e.preventDefault()
    this.setState({ inputOpen: !this.state.inputOpen })
  }

  render () {
    return (
      <form className='topbar__search material-form'>
        <TextField
          className={`material-form__field topbar__search-field${this.state.inputOpen ? ' topbar__search-field--open' : ''}`}/>
        <button className='topbar__btn' onClick={this.onInputOpen}>
          <SearchIcon/>
        </button>
      </form>
    )
  }
}
