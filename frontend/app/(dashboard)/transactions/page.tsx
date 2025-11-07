"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { getTransactionsAdvanced } from "@/lib/api"
import type { Transaction } from "@/types"

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    provider: "",
    status: "",
    currency: "",
  })

  useEffect(() => {
    fetchTransactions()
  }, [filters])

  const fetchTransactions = async () => {
    setLoading(true)
    const response = await getTransactionsAdvanced(filters)
    if (response.data?.transactions?.edges) {
      const txns = response.data.transactions.edges.map((e: any) => e.node)
      setTransactions(txns)
    }
    setLoading(false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-400"
      case "pending":
        return "text-yellow-400"
      case "failed":
        return "text-red-400"
      default:
        return "text-neutral-400"
    }
  }

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Transactions</h1>
        <p className="text-neutral-400">View and manage all transactions</p>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Filter by provider"
              value={filters.provider}
              onChange={(e) => setFilters({ ...filters, provider: e.target.value })}
              className="bg-background border-border"
            />
            <Input
              placeholder="Filter by status"
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="bg-background border-border"
            />
            <Input
              placeholder="Filter by currency"
              value={filters.currency}
              onChange={(e) => setFilters({ ...filters, currency: e.target.value })}
              className="bg-background border-border"
            />
            <Button onClick={fetchTransactions}>Apply Filters</Button>
          </div>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-neutral-400">Loading...</p>
          ) : transactions.length === 0 ? (
            <p className="text-neutral-400">No transactions found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-border">
                  <tr>
                    <th className="text-left py-3 px-4 text-neutral-400">Reference</th>
                    <th className="text-left py-3 px-4 text-neutral-400">Provider</th>
                    <th className="text-left py-3 px-4 text-neutral-400">Amount</th>
                    <th className="text-left py-3 px-4 text-neutral-400">Status</th>
                    <th className="text-left py-3 px-4 text-neutral-400">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id} className="border-b border-border hover:bg-background/50">
                      <td className="py-3 px-4 text-foreground font-mono text-xs">{tx.reference}</td>
                      <td className="py-3 px-4 text-foreground capitalize">{tx.provider}</td>
                      <td className="py-3 px-4 text-foreground">
                        {tx.amount} {tx.currency}
                      </td>
                      <td className={`py-3 px-4 capitalize font-semibold ${getStatusColor(tx.status)}`}>{tx.status}</td>
                      <td className="py-3 px-4 text-neutral-400">{new Date(tx.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
