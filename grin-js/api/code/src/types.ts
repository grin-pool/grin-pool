export interface ServerError extends Error {
  statusCode?: number
}