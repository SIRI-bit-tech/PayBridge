import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { PAYMENT_PROVIDERS, TRANSACTION_STATUSES, FILTER_CURRENCIES } from '@/constants'
import type { FilterOptions } from '@/types'

interface TransactionFiltersProps {
  filters: FilterOptions
  onFilterChange: (filters: FilterOptions) => void
  onReset: () => void
}

export function TransactionFilters({ filters, onFilterChange, onReset }: TransactionFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex-1 min-w-[200px]">
        <Select
          value={filters.provider || "all"}
          onValueChange={(value) => onFilterChange({ ...filters, provider: value === "all" ? "" : value })}
        >
          <SelectTrigger className="bg-background border-border">
            <SelectValue placeholder="All Providers" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Providers</SelectItem>
            {PAYMENT_PROVIDERS.map((provider) => (
              <SelectItem key={provider.id} value={provider.id}>
                {provider.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 min-w-[200px]">
        <Select
          value={filters.status || "all"}
          onValueChange={(value) => onFilterChange({ ...filters, status: value === "all" ? "" : value })}
        >
          <SelectTrigger className="bg-background border-border">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            {TRANSACTION_STATUSES.map((status) => (
              <SelectItem key={status.value} value={status.value}>
                {status.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 min-w-[200px]">
        <Select
          value={filters.currency || "all"}
          onValueChange={(value) => onFilterChange({ ...filters, currency: value === "all" ? "" : value })}
        >
          <SelectTrigger className="bg-background border-border">
            <SelectValue placeholder="All Currencies" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Currencies</SelectItem>
            {FILTER_CURRENCIES.map((currency) => (
              <SelectItem key={currency.value} value={currency.value}>
                {currency.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button variant="outline" onClick={onReset} className="border-border">
        Reset
      </Button>
    </div>
  )
}
