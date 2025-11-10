import { useEffect } from 'react'
import { useSocketIO } from './useSocketIO'

interface UseDashboardSocketIOOptions {
    onTransactionUpdate?: (data: any) => void
    onAnalyticsUpdate?: (data: any) => void
    onError?: (error: Error) => void
}

export function useDashboardSocketIO(options: UseDashboardSocketIOOptions = {}) {
    const { onTransactionUpdate, onAnalyticsUpdate, onError } = options

    const { socket, isConnected } = useSocketIO({
        autoConnect: true,
        onConnect: () => {
            console.log('Dashboard Socket.IO connected')
            // Join the dashboard room
            socket?.emit('join_dashboard')
        },
        onDisconnect: () => {
            console.log('Dashboard Socket.IO disconnected')
        },
        onError,
    })

    useEffect(() => {
        if (!socket) return

        // Listen for dashboard events
        socket.on('transaction_update', (data) => {
            console.log('Transaction update:', data)
            onTransactionUpdate?.(data)
        })

        socket.on('analytics_update', (data) => {
            console.log('Analytics update:', data)
            onAnalyticsUpdate?.(data)
        })

        socket.on('joined_dashboard', (data) => {
            console.log('Joined dashboard room:', data)
        })

        // Cleanup listeners on unmount
        return () => {
            socket.off('transaction_update')
            socket.off('analytics_update')
            socket.off('joined_dashboard')
            socket.emit('leave_dashboard')
        }
    }, [socket, onTransactionUpdate, onAnalyticsUpdate])

    return {
        isConnected,
        socket,
    }
}
