import { TransactionItem } from './TransactionItem'
import type { Transaction } from '@/types'

interface TransactionListProps {
  transactions: Transaction[]
  loading: boolean
}

export function TransactionList({ transactions, loading }: TransactionListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-neutral-400">No transactions found</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="border-b border-border">
          <tr>
            <th className="text-left py-3 px-4 text-neutral-400 font-medium">Reference</th>
            <th className="text-left py-3 px-4 text-neutral-400 font-medium">Provider</th>
            <th className="text-left py-3 px-4 text-neutral-400 font-medium">Amount</th>
            <th className="text-left py-3 px-4 text-neutral-400 font-medium">Status</th>
            <th className="text-left py-3 px-4 text-neutral-400 font-medium">Customer</th>
            <th className="text-left py-3 px-4 text-neutral-400 font-medium">Date</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <TransactionItem key={transaction.id} transaction={transaction} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
