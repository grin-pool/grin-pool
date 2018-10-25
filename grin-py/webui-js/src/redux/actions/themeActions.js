export const CHANGE_THEME_TO_DARK = 'CHANGE_THEME_TO_DARK'
export const CHANGE_THEME_TO_LIGHT = 'CHANGE_THEME_TO_LIGHT'

export function changeThemeToDark () {
  return {
    type: CHANGE_THEME_TO_DARK
  }
}

export function changeThemeToLight () {
  return {
    type: CHANGE_THEME_TO_LIGHT
  }
}
