// @flow
import { API_URL } from '../../config.js'
import { sha256 } from 'js-sha256'
import FormData from 'form-data'

export const createUser = (username: string, password: string, history: any) => async (dispatch, getState) => {
  dispatch({ type: 'IS_CREATING_ACCOUNT', data: true })
  try {
    const url = `${API_URL}pool/users`
    const formData = new FormData()
    const hashedPassword = sha256(password)
    formData.append('username', username)
    formData.append('password', hashedPassword)
    const createUserResponse = await fetch(url, {
      method: 'POST',
      body: formData
    })
    const createUserData = await createUserResponse.json()
    if (createUserData.username) {
      const hashedPassword = sha256(password)
      const auth = 'Basic ' + Buffer.from(username + ':' + hashedPassword).toString('base64')
      const url = `${API_URL}pool/users`
      const loginResponse = await fetch(url, {
        headers: {
          'Authorization': auth
        },
        method: 'GET'
      })
      console.log('auth is: ', auth)
      console.log('loginResponse is: ', loginResponse)
      const loginData = await loginResponse.json()
      dispatch({ type: 'ACCOUNT', data: { username, token: loginData.token } })
      history.push('/miner')
    } else {
      dispatch({ type: 'IS_CREATING_ACCOUNT', data: false })
    }
  } catch (e) {
    console.log('Error: ', e)
    dispatch({ type: 'IS_CREATING_ACCOUNT', data: false })
  }
}

export const login = (username: string, password: string, history) => async (dispatch, getState) => {
  dispatch({ type: 'IS_LOGGING_IN', data: true })
  try {
    const hashedPassword = sha256(password)
    const auth = 'Basic ' + Buffer.from(username + ':' + hashedPassword).toString('base64')
    const url = `${API_URL}pool/users`
    const loginResponse = await fetch(url, {
      headers: {
        'Authorization': auth
      },
      method: 'GET'
    })
    console.log('auth is: ', auth)
    console.log('loginResponse is: ', loginResponse)
    const loginData = await loginResponse.json()
    dispatch({ type: 'ACCOUNT', data: { username, token: loginData.token } })
    history.push('/miner')
  } catch (e) {
    console.log('Error: ', e)
    dispatch({ type: 'IS_LOGGING_IN', data: false })
  }
}
