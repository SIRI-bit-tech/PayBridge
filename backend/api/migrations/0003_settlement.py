# Generated migration for Settlement model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0002_alter_transaction_currency_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settlement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(0)])),
                ('currency', models.CharField(choices=[('NGN', 'Nigerian Naira'), ('GHS', 'Ghanaian Cedi'), ('KES', 'Kenyan Shilling'), ('UGX', 'Ugandan Shilling'), ('TZS', 'Tanzanian Shilling'), ('ETB', 'Ethiopian Birr'), ('ZAR', 'South African Rand'), ('USD', 'US Dollar'), ('GBP', 'British Pound'), ('EUR', 'Euro')], default='NGN', max_length=3)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('bank_account', models.CharField(blank=True, max_length=255)),
                ('reference', models.CharField(blank=True, max_length=100, unique=True)),
                ('failure_reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settlements', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'settlements',
                'ordering': ['-created_at'],
            },
        ),
    ]
