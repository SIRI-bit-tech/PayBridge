/**
 * Billing Socket.IO Hook
 * Real-time updates for billing, subscriptions, and usage
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import { io, Socket } from 'socket.io-client'

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:8001'

interface UseBillingSocketIOOptions {
  onPlanUpdate?: (data: any) => void
  onUsageUpdate?: (data: any) => void
  onLimitReached?: (data: any) => void
  onError?: (error: Event) => void
}

export function useBillingSocketIO(options?: UseBillingSocketIOOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const socketRef = useRef<Socket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5
  
  // Memoize options to prevent unnecessary reconnections
  const stableOptions = useRef(options)
  stableOptions.current = options

  const connect = useCallback(() => {
    // Prevent multiple simultaneous connections
    if (socketRef.current && socketRef.current.connected) {
      console.log('Socket.IO already connected')
      return
    }
    
    const token = localStorage.getItem('access_token')
    if (!token) {
      console.warn('No access token available for Socket.IO connection')
      return
    }

    console.log('Connecting to Socket.IO server for billing...')

    const socket = io(SOCKET_URL, {
      auth: {
        token,
      },
      transports: ['websocket', 'polling'],
      reconnection: false, // We'll handle reconnection manually
    })

    socket.on('connect', () => {
      console.log('Billing Socket.IO connected')
      setIsConnected(true)
      reconnectAttemptsRef.current = 0

      // Join billing room
      socket.emit('join_billing')
    })

    socket.on('joined_billing', (data) => {
      console.log('Joined billing room:', data.room)
    })

    socket.on('disconnect', (reason) => {
      console.log('Billing Socket.IO disconnected:', reason)
      setIsConnected(false)

      // Attempt to reconnect
      if (reconnectAttemptsRef.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
        console.log(`Attempting to reconnect in ${delay}ms...`)
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current++
          connect()
        }, delay)
      }
    })

    socket.on('connect_error', (error) => {
      console.error('Billing Socket.IO connection error:', error)
      setIsConnected(false)
      stableOptions.current?.onError?.(error as any)
    })

    // Billing event listeners
    socket.on('plan:update', (data) => {
      console.log('Plan update received:', data)
      stableOptions.current?.onPlanUpdate?.(data)
    })

    socket.on('usage:update', (data) => {
      console.log('Usage update received:', data)
      stableOptions.current?.onUsageUpdate?.(data)
    })

    socket.on('plan:limit_reached', (data) => {
      console.log('Limit reached:', data)
      stableOptions.current?.onLimitReached?.(data)
    })

    socketRef.current = socket
  }, []) // Empty dependency array since we use stableOptions ref

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    if (socketRef.current) {
      socketRef.current.emit('leave_billing')
      socketRef.current.disconnect()
      socketRef.current = null
    }

    setIsConnected(false)
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    socket: socketRef.current,
    reconnect: connect,
    disconnect,
  }
}
