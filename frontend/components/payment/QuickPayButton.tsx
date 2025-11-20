'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { CreditCard, Loader2 } from 'lucide-react';
import { createUnifiedPayment } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface QuickPayButtonProps {
  amount: number;
  currency?: string;
  customerEmail: string;
  description?: string;
  provider?: string;
  onSuccess?: (result: any) => void;
  onError?: (error: string) => void;
  className?: string;
  children?: React.ReactNode;
}

export default function QuickPayButton({
  amount,
  currency = 'NGN',
  customerEmail,
  description = 'Payment',
  provider,
  onSuccess,
  onError,
  className,
  children,
}: QuickPayButtonProps) {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handlePayment = async () => {
    setLoading(true);

    try {
      const result = await createUnifiedPayment({
        amount,
        currency,
        customer_email: customerEmail,
        callback_url: `${window.location.origin}/payment/callback`,
        provider,
        description,
      });

      const data = result.data as any;

      if (data?.success) {
        toast({
          title: 'Payment Initiated',
          description: `Transaction ID: ${data.transaction_id}`,
        });

        onSuccess?.(data);

        // Redirect to payment page
        if (data.authorization_url) {
          window.location.href = data.authorization_url;
        }
      } else {
        const errorMsg = data?.error || result.error || 'Payment failed';
        toast({
          title: 'Payment Failed',
          description: errorMsg,
          variant: 'destructive',
        });
        onError?.(errorMsg);
      }
    } catch (err: any) {
      const errorMsg = err.message || 'An unexpected error occurred';
      toast({
        title: 'Error',
        description: errorMsg,
        variant: 'destructive',
      });
      onError?.(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      onClick={handlePayment}
      disabled={loading}
      className={className}
    >
      {loading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Processing...
        </>
      ) : (
        <>
          <CreditCard className="mr-2 h-4 w-4" />
          {children || `Pay ${amount} ${currency}`}
        </>
      )}
    </Button>
  );
}
