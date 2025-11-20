'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CreditCard, CheckCircle2, XCircle } from 'lucide-react';

interface UnifiedPaymentFormProps {
  onSuccess?: (result: any) => void;
  onError?: (error: string) => void;
}

export default function UnifiedPaymentForm({ onSuccess, onError }: UnifiedPaymentFormProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  
  const [formData, setFormData] = useState({
    amount: '',
    currency: 'NGN',
    customer_email: '',
    callback_url: '',
    provider: '',
    description: '',
  });

  const providers = [
    { value: '', label: 'Auto-select (Recommended)' },
    { value: 'paystack', label: 'Paystack' },
    { value: 'flutterwave', label: 'Flutterwave' },
    { value: 'stripe', label: 'Stripe' },
    { value: 'mono', label: 'Mono' },
    { value: 'okra', label: 'Okra' },
    { value: 'chapa', label: 'Chapa' },
    { value: 'lazerpay', label: 'Lazerpay' },
  ];

  const currencies = [
    { value: 'NGN', label: 'Nigerian Naira (NGN)' },
    { value: 'USD', label: 'US Dollar (USD)' },
    { value: 'GHS', label: 'Ghanaian Cedi (GHS)' },
    { value: 'KES', label: 'Kenyan Shilling (KES)' },
    { value: 'ZAR', label: 'South African Rand (ZAR)' },
    { value: 'ETB', label: 'Ethiopian Birr (ETB)' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/transactions/pay/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          amount: parseFloat(formData.amount),
          currency: formData.currency,
          customer_email: formData.customer_email,
          callback_url: formData.callback_url || `${window.location.origin}/payment/callback`,
          provider: formData.provider || undefined, // Auto-select if empty
          description: formData.description,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
        onSuccess?.(data);
        
        // Redirect to payment page if authorization URL is provided
        if (data.authorization_url) {
          window.location.href = data.authorization_url;
        }
      } else {
        const errorMsg = data.error || 'Payment initiation failed';
        setError(errorMsg);
        onError?.(errorMsg);
      }
    } catch (err: any) {
      const errorMsg = err.message || 'An unexpected error occurred';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Unified Payment Gateway
        </CardTitle>
        <CardDescription>
          Single API for all payment providers - we handle the routing
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {result && (
          <Alert className="mb-4 border-green-500 bg-green-50">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              <div className="font-semibold">Payment initiated successfully!</div>
              <div className="text-sm mt-1">
                Transaction ID: {result.transaction_id}
                <br />
                Provider: {result.provider}
                <br />
                Amount: {result.amount} {result.currency}
              </div>
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="amount">Amount *</Label>
              <Input
                id="amount"
                type="number"
                step="0.01"
                placeholder="1500.00"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="currency">Currency *</Label>
              <Select
                value={formData.currency}
                onValueChange={(value) => setFormData({ ...formData, currency: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {currencies.map((curr) => (
                    <SelectItem key={curr.value} value={curr.value}>
                      {curr.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="customer_email">Customer Email *</Label>
            <Input
              id="customer_email"
              type="email"
              placeholder="customer@example.com"
              value={formData.customer_email}
              onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="provider">Payment Provider</Label>
            <Select
              value={formData.provider}
              onValueChange={(value) => setFormData({ ...formData, provider: value })}
            >
              <SelectTrigger>
                <SelectValue placeholder="Auto-select best provider" />
              </SelectTrigger>
              <SelectContent>
                {providers.map((prov) => (
                  <SelectItem key={prov.value} value={prov.value}>
                    {prov.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Leave empty to auto-select the best provider for you
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="callback_url">Callback URL (Optional)</Label>
            <Input
              id="callback_url"
              type="url"
              placeholder="https://yourapp.com/payment/callback"
              value={formData.callback_url}
              onChange={(e) => setFormData({ ...formData, callback_url: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Where to redirect after payment. Defaults to current domain.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (Optional)</Label>
            <Input
              id="description"
              placeholder="Product purchase, subscription, etc."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <CreditCard className="mr-2 h-4 w-4" />
                Initiate Payment
              </>
            )}
          </Button>
        </form>

        <div className="mt-6 p-4 bg-muted rounded-lg">
          <h4 className="font-semibold text-sm mb-2">How it works:</h4>
          <ul className="text-xs space-y-1 text-muted-foreground">
            <li>• Single API endpoint for all payment providers</li>
            <li>• Auto-selects best provider if not specified</li>
            <li>• Handles provider-specific routing automatically</li>
            <li>• Returns authorization URL for payment</li>
            <li>• Tracks transaction status in real-time</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
