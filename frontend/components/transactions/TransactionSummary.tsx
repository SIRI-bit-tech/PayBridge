import { Card, CardContent } from '@/components/ui/card'
import type { TransactionSummary as TransactionSummaryType } from '@/types'

interface TransactionSummaryProps {
  summary: TransactionSummaryType
}

export function TransactionSummary({ summary }: TransactionSummaryProps) {
  const stats = [
    {
      label: 'Total Transactions',
      value: summary.total_transactions.toLocaleString(),
      color: 'text-blue-400',
    },
    {
      label: 'Total Amount',
      value: summary.total_amount.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }),
      color: 'text-green-400',
      sublabel: 'Multi-currency',
    },
    {
      label: 'Successful',
      value: summary.successful_count.toLocaleString(),
      color: 'text-green-400',
    },
    {
      label: 'Pending',
      value: summary.pending_count.toLocaleString(),
      color: 'text-yellow-400',
    },
    {
      label: 'Failed',
      value: summary.failed_count.toLocaleString(),
      color: 'text-red-400',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label} className="bg-card border-border">
          <CardContent className="pt-6">
            <div className="space-y-2">
              <p className="text-sm text-neutral-400">{stat.label}</p>
              <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
              {'sublabel' in stat && (
                <p className="text-xs text-neutral-500">{stat.sublabel}</p>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
