"use client"

import { useEffect, useRef, useState, useCallback } from 'react'
import { useToast } from '@/hooks/use-toast'

interface WebSocketMessage {
    type: string
    data: any
}

export function useWebSocket(url: string) {
    const [isConnected, setIsConnected] = useState(false)
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)
    const { toast } = useToast()

    const connect = useCallback(() => {
        const token = localStorage.getItem('access_token')
        if (!token) {
            console.log('No access token, skipping WebSocket connection')
            return
        }

        try {
            const wsUrl = `${url}?token=${token}`
            const ws = new WebSocket(wsUrl)

            ws.onopen = () => {
                console.log('WebSocket connected')
                setIsConnected(true)
            }

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data) as WebSocketMessage
                    setLastMessage(message)

                    // Show toast notification for transaction updates
                    if (message.type === 'transaction_update') {
                        toast({
                            title: message.data.message || 'Transaction Update',
                            description: `${message.data.currency} ${message.data.amount} - ${message.data.status}`,
                        })
                    }
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error)
                }
            }

            ws.onerror = (error) => {
                console.error('WebSocket error:', error)
            }

            ws.onclose = () => {
                console.log('WebSocket disconnected')
                setIsConnected(false)

                // Attempt to reconnect after 5 seconds
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('Attempting to reconnect WebSocket...')
                    connect()
                }, 5000)
            }

            wsRef.current = ws
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error)
        }
    }, [url, toast])

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
        }
        if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
        }
    }, [])

    const sendMessage = useCallback((message: any) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message))
        }
    }, [])

    useEffect(() => {
        connect()
        return () => disconnect()
    }, [connect, disconnect])

    return {
        isConnected,
        lastMessage,
        sendMessage,
        reconnect: connect,
    }
}
