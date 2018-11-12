
import { connect } from 'react-redux'
import { LoginComponent } from '../../containers/Login/Login.js'
import { createUser, login } from '../actions/authActions.js'

const mapStateToProps = (state) => ({

})

const mapDispatchToProps = (dispatch) => {
  return {
    createUser: (username: string, password: string) => dispatch(createUser(username, password)),
    login: (username: string, password: string) => dispatch(login(username, password))
  }
}

export const LoginConnector = connect(mapStateToProps, mapDispatchToProps)(LoginComponent)
