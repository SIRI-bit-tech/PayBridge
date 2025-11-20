'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import QuickPayButton from '@/components/payment/QuickPayButton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Code2, Zap, ShoppingCart, Repeat } from 'lucide-react';

export default function PaymentExamplesPage() {
  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Payment Integration Examples</h1>
        <p className="text-muted-foreground">
          See how easy it is to integrate unified payments into your application
        </p>
      </div>

      <Tabs defaultValue="quick" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="quick">Quick Pay</TabsTrigger>
          <TabsTrigger value="ecommerce">E-commerce</TabsTrigger>
          <TabsTrigger value="subscription">Subscription</TabsTrigger>
          <TabsTrigger value="code">Code Examples</TabsTrigger>
        </TabsList>

        <TabsContent value="quick" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Quick Payment Button
              </CardTitle>
              <CardDescription>
                Single-click payment with auto-provider selection
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="text-lg">Basic Plan</CardTitle>
                    <CardDescription>Perfect for individuals</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold mb-4">₦5,000</div>
                    <QuickPayButton
                      amount={5000}
                      currency="NGN"
                      customerEmail="customer@example.com"
                      description="Basic Plan Subscription"
                      className="w-full"
                    />
                  </CardContent>
                </Card>

                <Card className="border-2 border-primary">
                  <CardHeader>
                    <CardTitle className="text-lg">Pro Plan</CardTitle>
                    <CardDescription>Most popular choice</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold mb-4">₦15,000</div>
                    <QuickPayButton
                      amount={15000}
                      currency="NGN"
                      customerEmail="customer@example.com"
                      description="Pro Plan Subscription"
                      provider="paystack"
                      className="w-full"
                    />
                  </CardContent>
                </Card>

                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="text-lg">Enterprise</CardTitle>
                    <CardDescription>For large teams</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold mb-4">₦50,000</div>
                    <QuickPayButton
                      amount={50000}
                      currency="NGN"
                      customerEmail="customer@example.com"
                      description="Enterprise Plan Subscription"
                      provider="flutterwave"
                      className="w-full"
                    />
                  </CardContent>
                </Card>
              </div>

              <div className="bg-muted p-4 rounded-lg">
                <h4 className="font-semibold text-sm mb-2">Implementation:</h4>
                <pre className="text-xs overflow-x-auto">
{`import QuickPayButton from '@/components/payment/QuickPayButton';

<QuickPayButton
  amount={5000}
  currency="NGN"
  customerEmail="customer@example.com"
  description="Basic Plan Subscription"
  onSuccess={(result) => console.log('Payment success:', result)}
  onError={(error) => console.error('Payment error:', error)}
/>`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ecommerce" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5 text-blue-500" />
                E-commerce Checkout
              </CardTitle>
              <CardDescription>
                Shopping cart with multiple items and unified payment
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center p-3 bg-muted rounded">
                  <div>
                    <div className="font-semibold">Product A</div>
                    <div className="text-sm text-muted-foreground">Quantity: 2</div>
                  </div>
                  <div className="font-semibold">₦3,000</div>
                </div>
                <div className="flex justify-between items-center p-3 bg-muted rounded">
                  <div>
                    <div className="font-semibold">Product B</div>
                    <div className="text-sm text-muted-foreground">Quantity: 1</div>
                  </div>
                  <div className="font-semibold">₦2,500</div>
                </div>
                <div className="flex justify-between items-center p-3 bg-muted rounded">
                  <div>
                    <div className="font-semibold">Shipping</div>
                  </div>
                  <div className="font-semibold">₦500</div>
                </div>
                <div className="flex justify-between items-center p-3 bg-primary/10 rounded font-bold">
                  <div>Total</div>
                  <div>₦6,000</div>
                </div>
              </div>

              <QuickPayButton
                amount={6000}
                currency="NGN"
                customerEmail="customer@example.com"
                description="E-commerce Order #12345"
                className="w-full"
              >
                Proceed to Checkout
              </QuickPayButton>

              <div className="bg-muted p-4 rounded-lg">
                <h4 className="font-semibold text-sm mb-2">Key Features:</h4>
                <ul className="text-xs space-y-1 text-muted-foreground">
                  <li>• Automatic provider selection based on currency</li>
                  <li>• Idempotency prevents duplicate orders</li>
                  <li>• Webhook notifications for order fulfillment</li>
                  <li>• Transaction tracking and analytics</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscription" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Repeat className="h-5 w-5 text-green-500" />
                Recurring Subscriptions
              </CardTitle>
              <CardDescription>
                Monthly/yearly subscription payments
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="border-2">
                  <CardHeader>
                    <CardTitle className="text-lg">Monthly</CardTitle>
                    <CardDescription>Billed monthly</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="text-3xl font-bold">₦9,999</div>
                      <div className="text-sm text-muted-foreground">per month</div>
                    </div>
                    <QuickPayButton
                      amount={9999}
                      currency="NGN"
                      customerEmail="customer@example.com"
                      description="Monthly Subscription"
                      className="w-full"
                    >
                      Subscribe Monthly
                    </QuickPayButton>
                  </CardContent>
                </Card>

                <Card className="border-2 border-green-500">
                  <CardHeader>
                    <CardTitle className="text-lg">Yearly</CardTitle>
                    <CardDescription>Save 20% with annual billing</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="text-3xl font-bold">₦95,990</div>
                      <div className="text-sm text-muted-foreground">per year</div>
                      <div className="text-xs text-green-600 font-semibold">Save ₦23,998</div>
                    </div>
                    <QuickPayButton
                      amount={95990}
                      currency="NGN"
                      customerEmail="customer@example.com"
                      description="Yearly Subscription"
                      className="w-full"
                    >
                      Subscribe Yearly
                    </QuickPayButton>
                  </CardContent>
                </Card>
              </div>

              <div className="bg-muted p-4 rounded-lg">
                <h4 className="font-semibold text-sm mb-2">Subscription Features:</h4>
                <ul className="text-xs space-y-1 text-muted-foreground">
                  <li>• Automatic renewal reminders</li>
                  <li>• Prorated upgrades/downgrades</li>
                  <li>• Grace period for failed payments</li>
                  <li>• Usage-based billing support</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="code" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code2 className="h-5 w-5 text-purple-500" />
                Integration Code Examples
              </CardTitle>
              <CardDescription>
                Copy-paste examples for quick integration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">React/Next.js Component</h3>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
{`import { createUnifiedPayment } from '@/lib/api';

export default function CheckoutButton() {
  const handlePayment = async () => {
    const result = await createUnifiedPayment({
      amount: 5000,
      currency: 'NGN',
      customer_email: 'customer@example.com',
      callback_url: window.location.origin + '/payment/callback',
      provider: 'paystack', // Optional
      description: 'Product purchase'
    });

    if (result.data?.success) {
      // Redirect to payment page
      window.location.href = result.data.authorization_url;
    }
  };

  return <button onClick={handlePayment}>Pay Now</button>;
}`}
                </pre>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Vanilla JavaScript</h3>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
{`async function initiatePayment() {
  const response = await fetch('/api/v1/transactions/pay/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + localStorage.getItem('token'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      amount: 5000,
      currency: 'NGN',
      customer_email: 'customer@example.com',
      callback_url: window.location.origin + '/callback',
      description: 'Product purchase'
    })
  });

  const data = await response.json();
  if (data.success) {
    window.location.href = data.authorization_url;
  }
}`}
                </pre>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Backend API Call (Node.js)</h3>
                <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
{`const axios = require('axios');

async function createPayment(userId, amount) {
  const response = await axios.post(
    'https://api.paybridge.com/api/v1/transactions/pay/',
    {
      amount: amount,
      currency: 'NGN',
      customer_email: 'customer@example.com',
      callback_url: 'https://yourapp.com/callback',
      description: 'Order payment'
    },
    {
      headers: {
        'Authorization': \`Bearer \${userToken}\`,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data;
}`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
