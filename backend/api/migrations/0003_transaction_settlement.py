# Generated migration to add settlement tracking to transactions

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_transaction_currency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='settlement',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='transactions',
                to='api.settlement'
            ),
        ),
    ]
