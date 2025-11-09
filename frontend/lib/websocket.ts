import { WS_BASE_URL } from "@/constants"

export class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private listeners: Map<string, Set<Function>> = new Map()

  constructor(private token: string) {}

  connect(path: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${WS_BASE_URL}${path}`)

        this.ws.onopen = () => {
          console.log("WebSocket connected")
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.emit(data.type, data)
          } catch (e) {
            console.error("WebSocket message parse error:", e)
          }
        }

        this.ws.onerror = (error) => {
          console.error("WebSocket error:", error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log("WebSocket closed, attempting reconnect...")
          this.attemptReconnect(path)
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  private attemptReconnect(path: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => this.connect(path), this.reconnectDelay)
    }
  }

  send(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }))
    }
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: Function) {
    this.listeners.get(event)?.delete(callback)
  }

  private emit(event: string, data: any) {
    this.listeners.get(event)?.forEach((callback) => callback(data))
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
