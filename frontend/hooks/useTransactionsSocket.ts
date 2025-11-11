import { useEffect, useCallback, useRef } from 'react'
import { useSocket } from './useSocket'
import type { Transaction } from '@/types'

interface UseTransactionsSocketOptions {
  onTransactionNew?: (transaction: Transaction) => void
  onTransactionUpdate?: (transaction: Transaction) => void
  onError?: (error: Error) => void
}

export function useTransactionsSocket(options: UseTransactionsSocketOptions = {}) {
  const { isConnected, emit, on, off } = useSocket({
    autoConnect: true,
  })

  const optionsRef = useRef(options)

  useEffect(() => {
    optionsRef.current = options
  }, [options])

  const handleTransactionNew = useCallback((data: Transaction) => {
    console.log('New transaction received:', data)
    optionsRef.current.onTransactionNew?.(data)
  }, [])

  const handleTransactionUpdate = useCallback((data: Transaction) => {
    console.log('Transaction update received:', data)
    optionsRef.current.onTransactionUpdate?.(data)
  }, [])

  useEffect(() => {
    if (isConnected) {
      // Join transactions room
      emit('join_transactions')
      
      // Listen for transaction events
      on('transaction:new', handleTransactionNew)
      on('transaction:update', handleTransactionUpdate)

      return () => {
        // Leave transactions room
        emit('leave_transactions')
        
        // Clean up listeners
        off('transaction:new', handleTransactionNew)
        off('transaction:update', handleTransactionUpdate)
      }
    }
  }, [isConnected, emit, on, off, handleTransactionNew, handleTransactionUpdate])
}

  return { isConnected }
}
