# Fixed migration for webhook system - no model deletions

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0006_billingsubscription_feature_payment_paymentattempt_and_more'),
    ]

    operations = [
        # Only drop tables that might actually exist, ignore errors
        migrations.RunSQL(
            sql="""
            DROP TABLE IF EXISTS webhook_events CASCADE;
            DROP TABLE IF EXISTS webhook_subscriptions CASCADE;
            DROP TABLE IF EXISTS webhook_delivery_logs CASCADE;
            DROP TABLE IF EXISTS webhook_delivery_metrics CASCADE;
            """,
            reverse_sql="SELECT 1;"
        ),
        
        # Create WebhookEvent model
        migrations.CreateModel(
            name='WebhookEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('provider', models.CharField(choices=[('paystack', 'Paystack'), ('flutterwave', 'Flutterwave'), ('stripe', 'Stripe'), ('mono', 'Mono')], db_index=True, max_length=20)),
                ('provider_event_id', models.CharField(db_index=True, max_length=255, unique=True)),
                ('canonical_event_type', models.CharField(db_index=True, max_length=100)),
                ('raw_payload', models.JSONField()),
                ('signature_valid', models.BooleanField(default=False)),
                ('received_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('processing_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('succeeded', 'Succeeded'), ('failed', 'Failed')], db_index=True, default='pending', max_length=20)),
                ('processing_error', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'webhook_events',
                'ordering': ['-received_at'],
            },
        ),
        
        # Create WebhookSubscription model
        migrations.CreateModel(
            name='WebhookSubscription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(validators=[django.core.validators.URLValidator()])),
                ('secret_key', models.CharField(max_length=255, unique=True)),
                ('selected_events', models.JSONField(default=list)),
                ('active', models.BooleanField(db_index=True, default=True)),
                ('last_delivery_status', models.CharField(choices=[('healthy', 'Healthy'), ('degraded', 'Degraded'), ('failing', 'Failing'), ('disabled', 'Disabled')], default='healthy', max_length=20)),
                ('last_delivery_at', models.DateTimeField(blank=True, null=True)),
                ('failure_count', models.IntegerField(default=0)),
                ('success_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webhook_subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'webhook_subscriptions',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create WebhookDeliveryLog model
        migrations.CreateModel(
            name='WebhookDeliveryLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('event_id', models.UUIDField(db_index=True)),
                ('event_type', models.CharField(max_length=100)),
                ('attempt_number', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed'), ('dead_letter', 'Dead Letter')], db_index=True, default='pending', max_length=20)),
                ('http_status_code', models.IntegerField(blank=True, null=True)),
                ('response_body', models.TextField(blank=True)),
                ('latency_ms', models.IntegerField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('next_retry_at', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('webhook_event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='api.webhookevent')),
                ('webhook_subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_logs', to='api.webhooksubscription')),
            ],
            options={
                'db_table': 'webhook_delivery_logs',
                'ordering': ['-created_at'],
            },
        ),
        
        # Create WebhookDeliveryMetrics model
        migrations.CreateModel(
            name='WebhookDeliveryMetrics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period_start', models.DateTimeField(db_index=True)),
                ('period_end', models.DateTimeField()),
                ('total_deliveries', models.IntegerField(default=0)),
                ('successful_deliveries', models.IntegerField(default=0)),
                ('failed_deliveries', models.IntegerField(default=0)),
                ('retry_count', models.IntegerField(default=0)),
                ('dead_letter_count', models.IntegerField(default=0)),
                ('avg_latency_ms', models.FloatField(default=0)),
                ('p95_latency_ms', models.FloatField(default=0)),
                ('p99_latency_ms', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('webhook_subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='api.webhooksubscription')),
            ],
            options={
                'db_table': 'webhook_delivery_metrics',
                'ordering': ['-period_start'],
            },
        ),
        
        # Add indexes
        migrations.AddIndex(
            model_name='webhookevent',
            index=models.Index(fields=['provider', '-received_at'], name='webhook_eve_provide_3503e3_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookevent',
            index=models.Index(fields=['canonical_event_type', '-received_at'], name='webhook_eve_canonic_790910_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookevent',
            index=models.Index(fields=['processing_status', '-received_at'], name='webhook_eve_process_1085da_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookevent',
            index=models.Index(fields=['provider_event_id'], name='webhook_eve_provide_ef7be8_idx'),
        ),
        migrations.AddIndex(
            model_name='webhooksubscription',
            index=models.Index(fields=['user', 'active'], name='webhook_sub_user_id_1c6876_idx'),
        ),
        migrations.AddIndex(
            model_name='webhooksubscription',
            index=models.Index(fields=['active', '-created_at'], name='webhook_sub_active_b2cf29_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdeliverylog',
            index=models.Index(fields=['webhook_subscription', '-created_at'], name='webhook_del_webhook_e82b2f_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdeliverylog',
            index=models.Index(fields=['status', '-created_at'], name='webhook_del_status_cc0947_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdeliverylog',
            index=models.Index(fields=['event_id', 'webhook_subscription'], name='webhook_del_event_i_f21fcd_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdeliverylog',
            index=models.Index(fields=['next_retry_at'], name='webhook_del_next_re_fa8c0f_idx'),
        ),
        
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='webhookdeliverymetrics',
            unique_together={('webhook_subscription', 'period_start')},
        ),
    ]