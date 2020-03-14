export const CHANGE_SIDEBAR_VISIBILITY = 'CHANGE_SIDEBAR_VISIBILITY'
export const CHANGE_MOBILE_SIDEBAR_VISIBILITY = 'CHANGE_MOBILE_SIDEBAR_VISIBILITY'

export function changeSidebarVisibility () {
  return {
    type: CHANGE_SIDEBAR_VISIBILITY
  }
}

export function changeMobileSidebarVisibility () {
  return {
    type: CHANGE_MOBILE_SIDEBAR_VISIBILITY
  }
}
