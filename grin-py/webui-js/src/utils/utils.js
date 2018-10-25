
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
