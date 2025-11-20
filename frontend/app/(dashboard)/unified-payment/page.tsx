'use client';

import { useState } from 'react';
import UnifiedPaymentForm from '@/components/payment/UnifiedPaymentForm';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Code, Zap, Shield, Globe } from 'lucide-react';

export default function UnifiedPaymentPage() {
  const [paymentResult, setPaymentResult] = useState<any>(null);

  const codeExample = `// Single API for all providers!
const response = await fetch('/api/v1/transactions/pay/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    amount: 1500,
    currency: 'NGN',
    customer_email: 'customer@example.com',
    callback_url: 'https://yourapp.com/callback',
    provider: 'paystack', // Optional - auto-selects if omitted
    description: 'Product purchase'
  })
});

const data = await response.json();
// Redirect to: data.authorization_url`;

  const curlExample = `curl -X POST https://api.paybridge.com/api/v1/transactions/pay/ \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 1500,
    "currency": "NGN",
    "customer_email": "customer@example.com",
    "callback_url": "https://yourapp.com/callback",
    "provider": "paystack"
  }'`;

  const pythonExample = `import requests

response = requests.post(
    'https://api.paybridge.com/api/v1/transactions/pay/',
    headers={
        'Authorization': 'Bearer YOUR_TOKEN',
        'Content-Type': 'application/json'
    },
    json={
        'amount': 1500,
        'currency': 'NGN',
        'customer_email': 'customer@example.com',
        'callback_url': 'https://yourapp.com/callback',
        'provider': 'paystack'  # Optional
    }
)

data = response.json()
print(data['authorization_url'])`;

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Unified Payment Gateway</h1>
        <p className="text-muted-foreground">
          One API endpoint for all payment providers - Paystack, Flutterwave, Stripe, Mono, and more
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <Zap className="h-8 w-8 text-yellow-500 mb-2" />
            <CardTitle className="text-lg">Single API</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              One endpoint for all providers. No need to learn multiple APIs.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <Globe className="h-8 w-8 text-blue-500 mb-2" />
            <CardTitle className="text-lg">Auto-Routing</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              We automatically route to the best provider for your transaction.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <Shield className="h-8 w-8 text-green-500 mb-2" />
            <CardTitle className="text-lg">Secure</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Idempotency keys prevent duplicate charges. Full audit trail.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <Code className="h-8 w-8 text-purple-500 mb-2" />
            <CardTitle className="text-lg">Simple</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Clean, consistent API across all providers. Easy integration.
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="test" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="test">Test Payment</TabsTrigger>
          <TabsTrigger value="docs">API Documentation</TabsTrigger>
        </TabsList>

        <TabsContent value="test" className="space-y-4">
          <UnifiedPaymentForm
            onSuccess={(result) => {
              setPaymentResult(result);
              console.log('Payment initiated:', result);
            }}
            onError={(error) => {
              console.error('Payment error:', error);
            }}
          />

          {paymentResult && (
            <Card>
              <CardHeader>
                <CardTitle>Payment Result</CardTitle>
                <CardDescription>Response from unified payment gateway</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                  {JSON.stringify(paymentResult, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="docs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Unified Payment Endpoint</CardTitle>
              <CardDescription>
                POST /api/v1/transactions/pay/ - Single endpoint for all providers
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Request Body</h3>
                <div className="bg-muted p-4 rounded-lg space-y-2 text-sm">
                  <div><code className="text-blue-600">amount</code> <span className="text-muted-foreground">(required)</span> - Payment amount</div>
                  <div><code className="text-blue-600">currency</code> <span className="text-muted-foreground">(required)</span> - Currency code (NGN, USD, etc.)</div>
                  <div><code className="text-blue-600">customer_email</code> <span className="text-muted-foreground">(required)</span> - Customer's email</div>
                  <div><code className="text-blue-600">callback_url</code> <span className="text-muted-foreground">(required)</span> - Redirect URL after payment</div>
                  <div><code className="text-blue-600">provider</code> <span className="text-muted-foreground">(optional)</span> - Provider name (auto-selects if omitted)</div>
                  <div><code className="text-blue-600">description</code> <span className="text-muted-foreground">(optional)</span> - Payment description</div>
                  <div><code className="text-blue-600">idempotency_key</code> <span className="text-muted-foreground">(optional)</span> - Prevent duplicate charges</div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Supported Providers</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {['Paystack', 'Flutterwave', 'Stripe', 'Mono', 'Okra', 'Chapa', 'Lazerpay'].map((provider) => (
                    <div key={provider} className="bg-muted px-3 py-2 rounded text-sm text-center">
                      {provider}
                    </div>
                  ))}
                </div>
              </div>

              <Tabs defaultValue="javascript" className="w-full">
                <TabsList>
                  <TabsTrigger value="javascript">JavaScript</TabsTrigger>
                  <TabsTrigger value="curl">cURL</TabsTrigger>
                  <TabsTrigger value="python">Python</TabsTrigger>
                </TabsList>

                <TabsContent value="javascript">
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                    {codeExample}
                  </pre>
                </TabsContent>

                <TabsContent value="curl">
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                    {curlExample}
                  </pre>
                </TabsContent>

                <TabsContent value="python">
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                    {pythonExample}
                  </pre>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
