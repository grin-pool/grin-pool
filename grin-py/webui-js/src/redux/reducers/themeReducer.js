import {
  CHANGE_THEME_TO_DARK,
  CHANGE_THEME_TO_LIGHT
} from '../actions/themeActions'

const initialState = {
  className: 'theme-dark'
}

export default function (state = initialState, action) {
  switch (action.type) {
    case CHANGE_THEME_TO_DARK:
      return { className: 'theme-dark' }
    case CHANGE_THEME_TO_LIGHT:
      return { className: 'theme-light' }
    default:
      return state
  }
}
