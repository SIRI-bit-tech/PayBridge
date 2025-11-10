import { useEffect } from 'react'
import { useSocketIO } from './useSocketIO'

interface UseApiKeysSocketIOOptions {
  onKeyCreated?: (data: any) => void
  onKeyRevoked?: (data: any) => void
  onKeyUsed?: (data: any) => void
  onError?: (error: Error) => void
}

export function useApiKeysSocketIO(options: UseApiKeysSocketIOOptions = {}) {
  const { onKeyCreated, onKeyRevoked, onKeyUsed, onError } = options

  const { socket, isConnected } = useSocketIO({
    autoConnect: true,
    onConnect: () => {
      console.log('API Keys Socket.IO connected')
      // Join the API keys room
      socket?.emit('join_api_keys')
    },
    onDisconnect: () => {
      console.log('API Keys Socket.IO disconnected')
    },
    onError,
  })

  useEffect(() => {
    if (!socket) return

    // Listen for API key events
    socket.on('api_key_created', (data) => {
      console.log('API key created:', data)
      onKeyCreated?.(data)
    })

    socket.on('api_key_revoked', (data) => {
      console.log('API key revoked:', data)
      onKeyRevoked?.(data)
    })

    socket.on('api_key_used', (data) => {
      console.log('API key used:', data)
      onKeyUsed?.(data)
    })

    socket.on('joined_api_keys', (data) => {
      console.log('Joined API keys room:', data)
    })

    // Cleanup listeners on unmount
    return () => {
      socket.off('api_key_created')
      socket.off('api_key_revoked')
      socket.off('api_key_used')
      socket.off('joined_api_keys')
      socket.emit('leave_api_keys')
    }
  }, [socket, onKeyCreated, onKeyRevoked, onKeyUsed])

  return {
    isConnected,
    socket,
  }
}
