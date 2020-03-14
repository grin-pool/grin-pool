
import { connect } from 'react-redux'
import { LoginComponent } from '../../containers/Login/Login.js'
import { createUser, login } from '../actions/authActions.js'

const mapStateToProps = (state) => ({
  isLoggingIn: state.auth.isLoggingIn,
  isCreatingAccount: state.auth.isCreatingAccount,
  authError: state.auth.authError
})

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    createUser: (username: string, password: string) => dispatch(createUser(username, password, ownProps.history)),
    login: (username: string, password: string) => dispatch(login(username, password, ownProps.history)),
    createAuthError: (message: string) => dispatch({ type: 'AUTH_ERROR', data: { authError: message } })
  }
}

export const LoginConnector = connect(mapStateToProps, mapDispatchToProps)(LoginComponent)
