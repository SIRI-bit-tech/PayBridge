# State-only migration - DB operations already performed in 0008_cleanup_indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_cleanup_indexes'),
    ]

    operations = [
        # Update Django's state to reflect the actual index names in the database
        migrations.AlterModelOptions(
            name='webhookdeliverylog',
            options={'db_table': 'webhook_delivery_logs', 'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='webhookevent',
            options={'db_table': 'webhook_events', 'ordering': ['-received_at']},
        ),
        migrations.AlterModelOptions(
            name='webhooksubscription',
            options={'db_table': 'webhook_subscriptions', 'ordering': ['-created_at']},
        ),
    ]
