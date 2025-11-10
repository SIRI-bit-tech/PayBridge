import { useEffect, useRef, useState } from 'react'
import { io, Socket } from 'socket.io-client'
import { WS_BASE_URL } from '@/constants'

interface UseSocketIOOptions {
  autoConnect?: boolean
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Error) => void
}

// Singleton socket instance to prevent multiple connections
let globalSocket: Socket | null = null
let connectionCount = 0

export function useSocketIO(options: UseSocketIOOptions = {}) {
  const { autoConnect = true, onConnect, onDisconnect, onError } = options
  const [isConnected, setIsConnected] = useState(false)
  const socketRef = useRef<Socket | null>(null)
  const callbacksRef = useRef({ onConnect, onDisconnect, onError })

  // Update callbacks ref without triggering reconnection
  useEffect(() => {
    callbacksRef.current = { onConnect, onDisconnect, onError }
  }, [onConnect, onDisconnect, onError])

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    
    if (!token) {
      console.warn('No access token available for Socket.IO connection')
      return
    }

    // Reuse existing socket if available
    if (globalSocket && globalSocket.connected) {
      console.log('Reusing existing Socket.IO connection:', globalSocket.id)
      socketRef.current = globalSocket
      setIsConnected(true)
      connectionCount++
      callbacksRef.current.onConnect?.()
      return () => {
        connectionCount--
        // Only disconnect if no other components are using it
        if (connectionCount === 0 && globalSocket) {
          console.log('Last component unmounted, disconnecting Socket.IO')
          globalSocket.disconnect()
          globalSocket = null
        }
      }
    }

    // Create new Socket.IO connection only if none exists
    console.log('Creating new Socket.IO connection')
    const socket = io(WS_BASE_URL, {
      auth: {
        token,
      },
      autoConnect,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ['websocket', 'polling'],
    })

    globalSocket = socket
    socketRef.current = socket
    connectionCount++

    // Connection event handlers
    socket.on('connect', () => {
      console.log('Socket.IO connected:', socket.id)
      setIsConnected(true)
      callbacksRef.current.onConnect?.()
    })

    socket.on('disconnect', (reason) => {
      console.log('Socket.IO disconnected:', reason)
      setIsConnected(false)
      callbacksRef.current.onDisconnect?.()
    })

    socket.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error)
      setIsConnected(false)
      callbacksRef.current.onError?.(error)
    })

    socket.on('connected', (data) => {
      console.log('Socket.IO server confirmed connection:', data)
    })

    // Cleanup on unmount
    return () => {
      connectionCount--
      console.log(`Component unmounted, connection count: ${connectionCount}`)
      
      // Only disconnect if no other components are using it
      if (connectionCount === 0 && globalSocket) {
        console.log('Last component unmounted, disconnecting Socket.IO')
        globalSocket.disconnect()
        globalSocket = null
        socketRef.current = null
      }
    }
  }, [autoConnect]) // Only depend on autoConnect, not callbacks

  return {
    socket: socketRef.current,
    isConnected,
  }
}
