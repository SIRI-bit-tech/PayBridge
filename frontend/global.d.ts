declare global {
  interface Window {
    ENV: {
      API_BASE_URL: string
      APP_NAME: string
      WS_BASE_URL: string
    }
  }
}

export {}
