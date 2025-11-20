'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { apiCall } from '@/lib/api';
import { PAYMENT_PROVIDERS } from '@/constants';
import { 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  ExternalLink, 
  Eye, 
  EyeOff,
  AlertCircle,
  Zap
} from 'lucide-react';
import { toast } from 'sonner';

interface PaymentProvider {
  id: string;
  provider: string;
  is_live: boolean;
  is_active: boolean;
  created_at: string;
}

const PROVIDERS = PAYMENT_PROVIDERS.map(({ id, name, logoUrl, docsUrl }) => ({
  id,
  label: name,
  logoUrl,
  docsUrl,
}));

export default function PaymentProvidersPage() {
  const [providers, setProviders] = useState<PaymentProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingProvider, setEditingProvider] = useState<string | null>(null);
  const [formData, setFormData] = useState({ public_key: '', secret_key: '' });
  const [saving, setSaving] = useState(false);
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    setLoading(true);
    const response = await apiCall<{ results: PaymentProvider[] }>('/payment-providers/');
    if (response.data) {
      setProviders(response.data.results || []);
    }
    setLoading(false);
  };

  const handleSaveProvider = async (providerId: string) => {
    if (!formData.public_key || !formData.secret_key) {
      toast.error('Please fill in all fields');
      return;
    }

    setSaving(true);
    const response = await apiCall('/payment-providers/', {
      method: 'POST',
      body: JSON.stringify({
        provider: providerId,
        public_key: formData.public_key,
        secret_key: formData.secret_key,
      }),
    });

    if (response.status === 201 || response.status === 200) {
      toast.success(`${providerId} provider configured successfully`);
      await fetchProviders();
      setEditingProvider(null);
      setFormData({ public_key: '', secret_key: '' });
    } else {
      toast.error(response.error || 'Failed to save provider');
    }
    setSaving(false);
  };

  const toggleSecretVisibility = (providerId: string) => {
    setShowSecrets((prev) => ({ ...prev, [providerId]: !prev[providerId] }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const configuredCount = providers.length;
  const activeCount = providers.filter((p) => p.is_active).length;

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Payment Providers</h1>
        <p className="text-muted-foreground mt-2">
          Configure your payment provider credentials for unified payment gateway
        </p>
      </div>

      {/* Info Alert */}
      <Alert>
        <Zap className="h-4 w-4" />
        <AlertDescription>
          <strong>Unified Payment Gateway:</strong> Configure your providers here, then use the{' '}
          <a href="/unified-payment" className="text-primary hover:underline">
            Unified Payment
          </a>{' '}
          page to accept payments from all providers with a single API.
        </AlertDescription>
      </Alert>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Providers</CardDescription>
            <CardTitle className="text-3xl">{PROVIDERS.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Configured</CardDescription>
            <CardTitle className="text-3xl text-primary">{configuredCount}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Active</CardDescription>
            <CardTitle className="text-3xl text-green-500">{activeCount}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Provider Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {PROVIDERS.map((provider) => {
          const configured = providers.find((p) => p.provider === provider.id);
          const isEditing = editingProvider === provider.id;
          const showSecret = showSecrets[provider.id];

          return (
            <Card key={provider.id} className={configured ? 'border-primary/50' : ''}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center overflow-hidden">
                      {provider.logoUrl ? (
                        <img
                          src={provider.logoUrl}
                          alt={`${provider.label} logo`}
                          className="h-full w-full object-contain p-2"
                        />
                      ) : (
                        <span className="text-lg font-bold text-muted-foreground">
                          {provider.label.charAt(0)}
                        </span>
                      )}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{provider.label}</CardTitle>
                      {configured && (
                        <Badge variant="default" className="mt-1">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Configured
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {isEditing ? (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-public`}>Public Key</Label>
                      <Input
                        id={`${provider.id}-public`}
                        type="text"
                        placeholder="pk_test_xxxxx"
                        value={formData.public_key}
                        onChange={(e) =>
                          setFormData({ ...formData, public_key: e.target.value })
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor={`${provider.id}-secret`}>Secret Key</Label>
                      <div className="relative">
                        <Input
                          id={`${provider.id}-secret`}
                          type={showSecret ? 'text' : 'password'}
                          placeholder="sk_test_xxxxx"
                          value={formData.secret_key}
                          onChange={(e) =>
                            setFormData({ ...formData, secret_key: e.target.value })
                          }
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => toggleSecretVisibility(provider.id)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        >
                          {showSecret ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </button>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleSaveProvider(provider.id)}
                        disabled={saving}
                        className="flex-1"
                      >
                        {saving ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Saving...
                          </>
                        ) : (
                          'Save'
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setEditingProvider(null);
                          setFormData({ public_key: '', secret_key: '' });
                        }}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <CardDescription>
                      {configured
                        ? 'Your credentials are securely stored and encrypted'
                        : 'Add your API credentials to enable this provider'}
                    </CardDescription>

                    <div className="flex gap-2">
                      <Button
                        onClick={() => {
                          setEditingProvider(provider.id);
                          setFormData({ public_key: '', secret_key: '' });
                        }}
                        className="flex-1"
                        variant={configured ? 'outline' : 'default'}
                      >
                        {configured ? 'Update' : 'Configure'}
                      </Button>
                      <Button
                        variant="outline"
                        size="icon"
                        asChild
                      >
                        <a
                          href={provider.docsUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </Button>
                    </div>

                    {configured && (
                      <div className="text-xs text-muted-foreground">
                        Configured on {new Date(configured.created_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Help Section */}
      <Card>
        <CardHeader>
          <CardTitle>Need Help?</CardTitle>
          <CardDescription>Getting your API credentials</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-semibold mb-2">Paystack</h4>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Log in to your Paystack dashboard</li>
                <li>Go to Settings → API Keys & Webhooks</li>
                <li>Copy your Public and Secret keys</li>
              </ol>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Flutterwave</h4>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Log in to your Flutterwave dashboard</li>
                <li>Go to Settings → API</li>
                <li>Copy your Public and Secret keys</li>
              </ol>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Stripe</h4>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Log in to your Stripe dashboard</li>
                <li>Go to Developers → API keys</li>
                <li>Copy your Publishable and Secret keys</li>
              </ol>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Mono</h4>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Log in to your Mono dashboard</li>
                <li>Go to Settings → Keys</li>
                <li>Copy your Public and Secret keys</li>
              </ol>
            </div>
          </div>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Security Note:</strong> Your API keys are encrypted and stored securely. Never
              share your secret keys publicly or commit them to version control.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}
