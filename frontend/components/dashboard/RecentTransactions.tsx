"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { graphQLQuery } from "@/lib/api"
import { useDashboardSocketIO } from "@/lib/useDashboardSocketIO"
import type { Transaction } from "@/types"
import { formatDistanceToNow } from "date-fns"

export function RecentTransactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTransactions = async () => {
      const query = `
        query {
          transactions {
            id
            reference
            amount
            currency
            status
            provider
            customerEmail
            description
            createdAt
          }
        }
      `
      const response = await graphQLQuery<any>(query)
      if (response.data?.transactions) {
        const txns = response.data.transactions.map((txn: any) => ({
          id: txn.id,
          reference: txn.reference,
          amount: parseFloat(txn.amount),
          currency: txn.currency,
          status: txn.status,
          provider: txn.provider,
          customer_email: txn.customerEmail,
          description: txn.description,
          created_at: txn.createdAt,
        }))
        setTransactions(txns)
      }
      setLoading(false)
    }

    fetchTransactions()
  }, [])

  // Real-time updates via Socket.IO
  useDashboardSocketIO({
    onTransactionUpdate: (data: any) => {
      const newTxn: Transaction = {
        id: data.id,
        reference: data.reference,
        amount: parseFloat(data.amount),
        currency: data.currency,
        status: data.status,
        provider: data.provider,
        customer_email: data.customer_email,
        description: data.description,
        created_at: data.created_at,
        fee: data.fee || 0,
        net_amount: data.net_amount || parseFloat(data.amount),
      }
      setTransactions((prev) => [newTxn, ...prev].slice(0, 10))
    },
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500/10 text-green-500"
      case "pending":
        return "bg-yellow-500/10 text-yellow-500"
      case "failed":
        return "bg-red-500/10 text-red-500"
      default:
        return "bg-gray-500/10 text-gray-500"
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">Loading transactions...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Transactions</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Reference</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Provider</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {transactions.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  No transactions yet
                </TableCell>
              </TableRow>
            ) : (
              transactions.map((txn) => (
                <TableRow key={txn.id}>
                  <TableCell className="font-mono text-sm">{txn.reference}</TableCell>
                  <TableCell>{txn.customer_email}</TableCell>
                  <TableCell>
                    {txn.currency} {txn.amount.toLocaleString()}
                  </TableCell>
                  <TableCell className="capitalize">{txn.provider}</TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(txn.status)}>{txn.status}</Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground text-sm">
                    {formatDistanceToNow(new Date(txn.created_at), { addSuffix: true })}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
