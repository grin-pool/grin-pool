
export const networkData = (state = 0, action) => {
  switch (action.type) {
    case 'NETWORK_DATA':
      return action.data
    default:
      return state
  }
}
