// Re-exporting useAuth from the auth provider for backward compatibility
import { useAuth as useAuthInternal } from '@/components/auth-provider';

export const useAuth = useAuthInternal;
