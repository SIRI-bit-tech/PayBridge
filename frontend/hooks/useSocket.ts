import { useEffect, useRef, useState, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_BASE_URL || 'http://localhost:8000'

interface UseSocketOptions {
  autoConnect?: boolean
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Error) => void
}

export function useSocket(options: UseSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false)
  const socketRef = useRef<Socket | null>(null)
  const stableOptions = useRef(options)
  stableOptions.current = options

  const connect = useCallback(() => {
    if (socketRef.current?.connected) {
      console.log('Socket already connected')
      return
    }

    const token = localStorage.getItem('access_token')
    if (!token) {
      console.warn('No access token available for Socket.IO connection')
      return
    }

    console.log('Connecting to Socket.IO server...')
    
    const socket = io(WS_BASE_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    })

    socket.on('connect', () => {
      console.log('Socket.IO connected')
      setIsConnected(true)
      stableOptions.current.onConnect?.()
    })

    socket.on('disconnect', () => {
      console.log('Socket.IO disconnected')
      setIsConnected(false)
      stableOptions.current.onDisconnect?.()
    })

    socket.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error)
      stableOptions.current.onError?.(error)
    })

    socketRef.current = socket
  }, [])

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect()
      socketRef.current = null
    }
  }, [])

  const emit = useCallback((event: string, data?: any) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data)
    } else {
      console.warn('Socket not connected, cannot emit event:', event)
    }
  }, [])

  const on = useCallback((event: string, handler: (...args: any[]) => void) => {
    if (socketRef.current) {
      socketRef.current.on(event, handler)
    }
  }, [])

  const off = useCallback((event: string, handler?: (...args: any[]) => void) => {
    if (socketRef.current) {
      if (handler) {
        socketRef.current.off(event, handler)
      } else {
        socketRef.current.off(event)
      }
    }
  }, [])

  useEffect(() => {
    if (options.autoConnect !== false) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [connect, disconnect, options.autoConnect])

  return {
    isConnected,
    connect,
    disconnect,
    emit,
    on,
    off,
    socket: socketRef.current,
  }
}
