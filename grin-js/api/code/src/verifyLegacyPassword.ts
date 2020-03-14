const verifySpawn = require('child_process').spawn
const verifyPs = require('python-shell')
const fs = require('fs')

const getLegacyPassword = (pwd: string, salt: string, rounds: number): Promise<string | Error> => {
  const options = {
    scriptPath: '../py/',
    pythonOptions: ['-u'],
    args: [pwd, salt, rounds]
  }
  const path = '../py/getLegacyPassword.py'
  const fileExistence = fs.existsSync(path)
  // console.log('file exists? ', fileExistence)

  return new Promise ((resolve, reject) => {
    // console.log('pwd is: ', pwd, ' salt is: ', salt, ' rounds are: ', rounds)
    verifyPs.PythonShell.run('getLegacyPassword.py', options, (error, results) => {
      console.log('verifyLegacyPassword results are: ', results)
      if (error) {
        console.log('pythonShell error: ', error)
        reject(error)
      }
      resolve(results[0])
    })
  })
}

module.exports = getLegacyPassword