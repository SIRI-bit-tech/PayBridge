import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from django.db import connection
from django.db.models import Avg, Sum, Count, StdDev
from datetime import datetime, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """Anomaly detection using Isolation Forest ML model"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=0.1, random_state=42)
    
    def extract_transaction_features(self, transaction):
        """Extract ML features from transaction"""
        user = transaction.user
        
        # Get user statistics
        user_stats = self._get_user_statistics(user)
        
        features = {
            'amount': float(transaction.amount),
            'hour_of_day': transaction.created_at.hour,
            'day_of_week': transaction.created_at.weekday(),
            'is_weekend': 1 if transaction.created_at.weekday() >= 5 else 0,
            'user_avg_transaction': float(user_stats['avg_amount'] or 0),
            'user_transaction_std': float(user_stats['std_amount'] or 1),
            'user_transaction_count': user_stats['transaction_count'],
            'velocity_last_hour': self._get_velocity(user, 'hour'),
            'velocity_last_day': self._get_velocity(user, 'day'),
            'phone_new': 1 if self._is_new_phone(transaction) else 0,
            'currency_mismatch': 1 if self._is_currency_anomaly(user, transaction) else 0,
        }
        
        return features
    
    def score_transaction(self, transaction):
        """Score transaction for fraud probability (0-1)"""
        try:
            features = self.extract_transaction_features(transaction)
            feature_array = np.array([list(features.values())])
            
            # Normalize features
            feature_scaled = self.scaler.fit_transform(feature_array)
            
            # Get anomaly score from Isolation Forest
            score = self.model.decision_function(feature_scaled)[0]
            
            # Convert to probability (0-1)
            fraud_probability = 1 / (1 + np.exp(score))
            
            return {
                'fraud_score': float(fraud_probability),
                'is_suspicious': fraud_probability > 0.7,
                'features': features,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Fraud detection error: {str(e)}")
            return {'fraud_score': 0.0, 'is_suspicious': False}
    
    def flag_transaction(self, transaction, fraud_score):
        """Flag transaction for manual review if suspicious"""
        if fraud_score['is_suspicious']:
            transaction.metadata = transaction.metadata or {}
            transaction.metadata['fraud_flag'] = True
            transaction.metadata['fraud_score'] = fraud_score['fraud_score']
            transaction.metadata['review_needed'] = True
            transaction.save()
            
            # Log to audit
            logger.warning(f"Fraudulent transaction flagged: {transaction.reference}")
            return True
        return False
    
    def _get_user_statistics(self, user):
        """Get user transaction statistics"""
        stats = user.transactions.filter(
            status='completed'
        ).aggregate(
            avg_amount=Avg('amount'),
            std_amount=StdDev('amount'),
            count=Count('id'),
        )
        return stats
    
    def _get_velocity(self, user, period):
        """Get transaction velocity (transactions in period)"""
        now = datetime.now()
        if period == 'hour':
            start = now - timedelta(hours=1)
        else:  # day
            start = now - timedelta(days=1)
        
        return user.transactions.filter(
            created_at__gte=start
        ).count()
    
    def _is_new_phone(self, transaction):
        """Check if phone is new for user"""
        if not transaction.customer_phone:
            return False
        
        previous = transaction.user.transactions.filter(
            customer_phone=transaction.customer_phone
        ).exclude(id=transaction.id).exists()
        
        return not previous
    
    def _is_currency_anomaly(self, user, transaction):
        """Check if currency is unusual for user"""
        common_currency = user.transactions.values('currency').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        if not common_currency:
            return False
        
        return transaction.currency != common_currency['currency']


# PostgreSQL trigger for anomaly detection
FRAUD_DETECTION_TRIGGER = """
CREATE OR REPLACE FUNCTION detect_fraud_anomalies()
RETURNS TRIGGER AS $$
DECLARE
    user_avg_amount DECIMAL;
    user_std_amount DECIMAL;
    z_score DECIMAL;
BEGIN
    -- Get user statistics
    SELECT AVG(amount), STDDEV_POP(amount) INTO user_avg_amount, user_std_amount
    FROM api_transaction
    WHERE user_id = NEW.user_id AND status = 'completed'
    AND created_at > NOW() - INTERVAL '30 days';
    
    -- Calculate Z-score
    IF user_std_amount > 0 THEN
        z_score := (NEW.amount - user_avg_amount) / user_std_amount;
        
        -- Flag if Z-score > 3 (99.7% confidence outlier)
        IF ABS(z_score) > 3 THEN
            NEW.metadata = jsonb_set(
                COALESCE(NEW.metadata, '{}'::jsonb),
                '{fraud_flag,z_score}',
                to_jsonb(z_score)
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER transaction_fraud_detection
BEFORE INSERT ON api_transaction
FOR EACH ROW
EXECUTE FUNCTION detect_fraud_anomalies();
"""
