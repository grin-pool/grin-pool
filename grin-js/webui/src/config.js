const env = process.env.NODE_ENV

let URL = ''
let URL_V2 = ''

if (env === 'production') {
  URL = 'https://api.mwfloopool.com/'
  URL_V2 = 'https://api.mwfloopool.com/v2/'
} else if (env === 'development') {
  URL = 'https://api.mwfloopool.com/'
  URL_V2 = 'http://localhost:3009/'
}

console.log('process.env.NODE_ENV is: ', process.env.NODE_ENV, ' and env is: ', env, ' URL is: ', URL, ' an URL_V2 is: ', URL_V2, ' process.env is: ', process.env)
export const API_URL = URL
export const API_URL_V2 = URL_V2
