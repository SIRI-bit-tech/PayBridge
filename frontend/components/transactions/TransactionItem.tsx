import type { Transaction } from '@/types'

interface TransactionItemProps {
  transaction: Transaction
}

export function TransactionItem({ transaction }: TransactionItemProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-400 bg-green-400/10'
      case 'pending':
        return 'text-yellow-400 bg-yellow-400/10'
      case 'failed':
        return 'text-red-400 bg-red-400/10'
      case 'refunded':
        return 'text-blue-400 bg-blue-400/10'
      case 'cancelled':
        return 'text-gray-400 bg-gray-400/10'
      default:
        return 'text-neutral-400 bg-neutral-400/10'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  return (
    <tr className="border-b border-border hover:bg-background/50 transition-colors">
      <td className="py-4 px-4">
        <div className="font-mono text-xs text-foreground">{transaction.reference}</div>
        <div className="text-xs text-neutral-400 mt-1">{transaction.id.slice(0, 8)}</div>
      </td>
      <td className="py-4 px-4">
        <div className="capitalize text-foreground font-medium">{transaction.provider}</div>
      </td>
      <td className="py-4 px-4">
        <div className="text-foreground font-semibold">
          {transaction.amount.toLocaleString()} {transaction.currency}
        </div>
        {transaction.fee > 0 && (
          <div className="text-xs text-neutral-400 mt-1">
            Fee: {transaction.fee.toLocaleString()} {transaction.currency}
          </div>
        )}
      </td>
      <td className="py-4 px-4">
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${getStatusColor(
            transaction.status
          )}`}
        >
          {transaction.status}
        </span>
      </td>
      <td className="py-4 px-4">
        <div className="text-foreground">{transaction.customer_email}</div>
        {transaction.customer_name && (
          <div className="text-xs text-neutral-400 mt-1">{transaction.customer_name}</div>
        )}
      </td>
      <td className="py-4 px-4 text-neutral-400 text-sm">{formatDate(transaction.created_at)}</td>
    </tr>
  )
}
