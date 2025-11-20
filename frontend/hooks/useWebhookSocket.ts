"use client"

import { useEffect, useState } from 'react'
import { io, Socket } from 'socket.io-client'

const SOCKET_URL = process.env.NEXT_PUBLIC_WS_BASE_URL || 'http://localhost:8000'

interface WebhookDeliveryUpdate {
  subscription_id: string
  event_id: string
  status: 'pending' | 'success' | 'failed' | 'dead_letter'
  attempt: number
  timestamp: string
}

interface WebhookEventUpdate {
  type: string
  event_id: string
  provider: string
  timestamp: string
}

export function useWebhookSocket() {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [connected, setConnected] = useState(false)
  const [deliveryUpdates, setDeliveryUpdates] = useState<WebhookDeliveryUpdate[]>([])
  const [eventUpdates, setEventUpdates] = useState<WebhookEventUpdate[]>([])

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) return

    const socketInstance = io(SOCKET_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
    })

    socketInstance.on('connect', () => {
      console.log('Webhook Socket connected')
      setConnected(true)
    })

    socketInstance.on('disconnect', () => {
      console.log('Webhook Socket disconnected')
      setConnected(false)
    })

    // Listen for webhook delivery updates
    socketInstance.on('webhook_deliveries', (data: WebhookDeliveryUpdate) => {
      console.log('Webhook delivery update:', data)
      setDeliveryUpdates((prev) => [data, ...prev].slice(0, 50)) // Keep last 50
    })

    // Listen for webhook event updates
    socketInstance.on('bridge_events', (data: WebhookEventUpdate) => {
      console.log('Webhook event update:', data)
      setEventUpdates((prev) => [data, ...prev].slice(0, 50)) // Keep last 50
    })

    setSocket(socketInstance)

    return () => {
      socketInstance.disconnect()
    }
  }, [])

  return {
    socket,
    connected,
    deliveryUpdates,
    eventUpdates,
  }
}
