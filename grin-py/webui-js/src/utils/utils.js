
export const ellipsizeString = (input, length) => {
  const inputLength = input.length
  const halfway = length / 2
  const firstHalf = input.slice(0, halfway)
  const secondHalf = input.slice(inputLength - halfway, inputLength)
  const output = `${firstHalf}...${secondHalf}`
  return output
}

export const getTokenInfoFromCurrencyCode = (currencyCode, state) => {
  const tokensDirectory = state.tokens.tokensDirectory
  if (!tokensDirectory) return null
  const tokenInfo = tokensDirectory.find(token => token.symbol === currencyCode)
  if (!tokenInfo) return null
  return tokenInfo
}

export const getTokenInfoFromAddress = (address, state) => {
  const tokensDirectory = state.tokens.tokensDirectory
  if (!tokensDirectory) return null
  const tokenInfo = tokensDirectory.find(token => token.address.toLowerCase() === address.toLowerCase())
  if (!tokenInfo) return null
  return tokenInfo
}

export const getTimeMeasurement = (inMinutes: number): string => {
  switch (true) {
    case inMinutes < 1:
      return 'seconds'

    case inMinutes < 60:
      return 'minutes'

    case inMinutes < 1440:
      return 'hours'

    case inMinutes <= 84960:
      return 'days'

    default:
      return ''
  }
}

export const getTimeWithMeasurement = (inMinutes: number): { measurement: string, value: number } => {
  const measurement = getTimeMeasurement(inMinutes)

  const measurements = {
    seconds (minutes) {
      const val = Math.round(minutes * 60)
      return val
    },
    minutes (minutes) {
      return minutes
    },
    hours (minutes) {
      return minutes / 60
    },
    days (minutes) {
      return minutes / 24 / 60
    }
  }
  const strategy = measurements[measurement]

  if (!strategy) {
    console.error(`No strategy for particular measurement: ${measurement}`)
    return { measurement: '', value: Infinity }
  }
  return {
    measurement,
    value: strategy(inMinutes)
  }
}
export const getTimeInMinutes = (params: { measurement: string, value: number }): number => {
  const { measurement, value } = params
  const measurementStrategies = {
    seconds (v) {
      const val = Math.round(v / 60 * 100) / 100
      return val
    },
    minutes (v) {
      return v
    },
    hours (v) {
      return v * 60
    },
    days (v) {
      return v * 24 * 60
    }
  }
  const strategy = measurementStrategies[measurement]

  if (!strategy) {
    console.error(`No strategy for particular measurement: ${measurement}`)
    return Infinity
  }
  return strategy(value)
}

export function secondsToHms (d) {
  d = Number(d)
  const h = Math.floor(d / 3600)
  const m = Math.floor(d % 3600 / 60)
  const s = Math.floor(d % 3600 % 60)
  let sDisplay = ''
  const hDisplay = h > 0 ? h + 'h ' : ''
  const mDisplay = m > 0 ? m + 'm ' : ''
  if (h === 0) {
    sDisplay = s > 0 ? s + 's ' : ''
  }

  return hDisplay + mDisplay + sDisplay
}

export const basicAuth = (token) => {
  const auth = 'Basic ' + Buffer.from(token + ':' + 'random').toString('base64')
  return auth
}
