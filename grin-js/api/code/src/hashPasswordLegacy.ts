const spawn = require('child_process').spawn
const ps = require('python-shell')

const hashPasswordLegacy = (password: string, legacyHash: string) => {
  const options = {
    scriptPath: '../../../grin-py/',
    pythonOptions: ['-u'],
    args: [password, legacyHash]
  }
  return new Promise ((resolve, reject) => {
    ps.PythonShell.run('hashPassword.py', options, (error, results) => {
      // console.log('hashPaswordLegacy results are: ', results)
      if (error) reject(error)
      resolve(results[0])
    })
  })
}

module.exports = hashPasswordLegacy