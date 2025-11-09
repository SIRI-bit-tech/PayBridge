"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { apiCall } from "@/lib/api"
import { DollarSign, Calendar, TrendingUp } from "lucide-react"
import { formatDistanceToNow } from "date-fns"

interface SettlementData {
  available_balance: number
  pending_balance: number
  currency: string
  next_settlement_date: string
  last_settlement_date: string | null
  last_settlement_amount: number | null
}

export function SettlementSummary() {
  const [settlement, setSettlement] = useState<SettlementData | null>(null)
  const [loading, setLoading] = useState(true)
  const [withdrawing, setWithdrawing] = useState(false)

  useEffect(() => {
    fetchSettlement()
  }, [])

  const fetchSettlement = async () => {
    const response = await apiCall<SettlementData>("/settlements/balance/")
    if (response.data) {
      setSettlement(response.data)
    }
    setLoading(false)
  }

  const handleWithdraw = async () => {
    setWithdrawing(true)
    const response = await apiCall("/settlements/withdraw/", {
      method: "POST",
    })
    if (response.data) {
      await fetchSettlement()
    }
    setWithdrawing(false)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Settlement Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">Loading settlement data...</div>
        </CardContent>
      </Card>
    )
  }

  if (!settlement) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Settlement Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-muted-foreground">No settlement data available</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Settlement Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <DollarSign className="h-4 w-4" />
              Available Balance
            </div>
            <div className="text-2xl font-bold text-green-500">
              {settlement.currency} {settlement.available_balance.toLocaleString()}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              Pending Balance
            </div>
            <div className="text-2xl font-bold text-yellow-500">
              {settlement.currency} {settlement.pending_balance.toLocaleString()}
            </div>
          </div>
        </div>

        <div className="space-y-3 pt-4 border-t border-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Next Settlement
            </span>
            <span className="font-medium">
              {formatDistanceToNow(new Date(settlement.next_settlement_date), { addSuffix: true })}
            </span>
          </div>

          {settlement.last_settlement_date && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Last Settlement</span>
              <span className="font-medium">
                {settlement.currency} {settlement.last_settlement_amount?.toLocaleString()}
              </span>
            </div>
          )}
        </div>

        <Button
          onClick={handleWithdraw}
          disabled={settlement.available_balance === 0 || withdrawing}
          className="w-full"
        >
          {withdrawing ? "Processing..." : "Initiate Withdrawal"}
        </Button>
      </CardContent>
    </Card>
  )
}
