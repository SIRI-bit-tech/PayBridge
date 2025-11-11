"use client"

import { useEffect, useState, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getTransactions } from "@/lib/api"
import { useTransactionsSocket } from "@/hooks/useTransactionsSocket"
import { TransactionSummary } from "@/components/transactions/TransactionSummary"
import { TransactionFilters } from "@/components/transactions/TransactionFilters"
import { TransactionList } from "@/components/transactions/TransactionList"
import { RealTimeIndicator } from "@/components/transactions/RealTimeIndicator"
import type { Transaction, FilterOptions, TransactionSummary as TransactionSummaryType } from "@/types"

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [filteredTransactions, setFilteredTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<FilterOptions>({
    provider: "",
    status: "",
    currency: "",
  })
  const [summary, setSummary] = useState<TransactionSummaryType>({
    total_transactions: 0,
    total_amount: 0,
    successful_count: 0,
    pending_count: 0,
    failed_count: 0,
    refunded_count: 0,
  })

  // Fetch initial transactions
  const fetchTransactions = useCallback(async () => {
    setLoading(true)
    try {
      const response = await getTransactions()
      if (response.data) {
        const txns = Array.isArray(response.data) ? response.data : []
        setTransactions(txns)
        calculateSummary(txns)
      }
    } catch (error) {
      console.error("Failed to fetch transactions:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  // Calculate summary statistics
  const calculateSummary = useCallback((txns: Transaction[]) => {
    const newSummary: TransactionSummaryType = {
      total_transactions: txns.length,
      total_amount: txns.reduce((sum, tx) => sum + Number(tx.amount), 0),
      successful_count: txns.filter((tx) => tx.status === "completed").length,
      pending_count: txns.filter((tx) => tx.status === "pending").length,
      failed_count: txns.filter((tx) => tx.status === "failed").length,
      refunded_count: txns.filter((tx) => tx.status === "refunded").length,
    }
    setSummary(newSummary)
  }, [])

  // Handle new transaction from Socket.IO
  const handleTransactionNew = useCallback((transaction: Transaction) => {
    setTransactions((prev) => {
      const exists = prev.find((tx) => tx.id === transaction.id)
      if (exists) return prev
      const updated = [transaction, ...prev]
      calculateSummary(updated)
      return updated
    })
  }, [calculateSummary])

  // Handle transaction update from Socket.IO
  const handleTransactionUpdate = useCallback((transaction: Transaction) => {
    setTransactions((prev) => {
      const updated = prev.map((tx) =>
        tx.id === transaction.id ? { ...tx, ...transaction } : tx
      )
      calculateSummary(updated)
      return updated
    })
  }, [calculateSummary])

  // Real-time Socket.IO connection
  const { isConnected } = useTransactionsSocket({
    onTransactionNew: handleTransactionNew,
    onTransactionUpdate: handleTransactionUpdate,
  })

  // Apply filters
  useEffect(() => {
    let filtered = [...transactions]

    if (filters.provider) {
      filtered = filtered.filter((tx) => tx.provider === filters.provider)
    }

    if (filters.status) {
      filtered = filtered.filter((tx) => tx.status === filters.status)
    }

    if (filters.currency) {
      filtered = filtered.filter((tx) => tx.currency === filters.currency)
    }

    setFilteredTransactions(filtered)
  }, [transactions, filters])

  // Initial fetch
  useEffect(() => {
    fetchTransactions()
  }, [fetchTransactions])

  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters)
  }

  const handleResetFilters = () => {
    setFilters({
      provider: "",
      status: "",
      currency: "",
    })
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Transactions</h1>
          <p className="text-neutral-400">Real-time transaction monitoring and analytics</p>
        </div>
        <RealTimeIndicator isConnected={isConnected} />
      </div>

      {/* Summary Stats */}
      <TransactionSummary summary={summary} />

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <TransactionFilters
            filters={filters}
            onFilterChange={handleFilterChange}
            onReset={handleResetFilters}
          />
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>
            Recent Transactions
            {filteredTransactions.length !== transactions.length && (
              <span className="text-sm font-normal text-neutral-400 ml-2">
                ({filteredTransactions.length} of {transactions.length})
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <TransactionList transactions={filteredTransactions} loading={loading} />
        </CardContent>
      </Card>
    </div>
  )
}
