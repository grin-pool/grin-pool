const usernameSpawn = require('child_process').spawn
const usernamePs = require('python-shell')

const getUserByUsername = (username: string, password: string) => {
  const options = {
    scriptPath: '../../../grin-py/',
    pythonOptions: ['-u'],
    args: [username, password]
  }
  return new Promise ((resolve, reject) => {
    // console.log('getUserByUsername username is: ', username, ' and password is: ', password)
    usernamePs.PythonShell.run('getUserByUsername.py', options, (error, results) => {
      // console.log('getUserByUsername results are: ', results)
      if (error) reject(error)
      resolve(results[0])
    })
  })
}

module.exports = getUserByUsername