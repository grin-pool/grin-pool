import { colorTheme } from '../../custom/custom.js'

const initialState = {
  className: colorTheme
}

export default function (state = initialState, action) {
  switch (action.type) {
    default:
      return state
  }
}
