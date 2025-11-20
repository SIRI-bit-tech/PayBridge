# Manual migration to clean up indexes without touching subscription field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_webhook_system'),
    ]

    operations = [
        # Just rename indexes, skip the subscription field removal since it doesn't exist
        migrations.RunSQL(
            sql="""
            -- Rename webhook delivery log indexes
            ALTER INDEX IF EXISTS webhook_del_webhook_idx RENAME TO webhook_del_webhook_e82b2f_idx;
            ALTER INDEX IF EXISTS webhook_del_status_idx RENAME TO webhook_del_status_cc0947_idx;
            ALTER INDEX IF EXISTS webhook_del_event_i_idx RENAME TO webhook_del_event_i_f21fcd_idx;
            ALTER INDEX IF EXISTS webhook_del_next_re_idx RENAME TO webhook_del_next_re_fa8c0f_idx;
            
            -- Rename webhook event indexes
            ALTER INDEX IF EXISTS webhook_eve_provide_idx RENAME TO webhook_eve_provide_3503e3_idx;
            ALTER INDEX IF EXISTS webhook_eve_canonic_idx RENAME TO webhook_eve_canonic_790910_idx;
            ALTER INDEX IF EXISTS webhook_eve_process_idx RENAME TO webhook_eve_process_1085da_idx;
            
            -- Rename webhook subscription indexes
            ALTER INDEX IF EXISTS webhook_sub_user_id_idx RENAME TO webhook_sub_user_id_1c6876_idx;
            ALTER INDEX IF EXISTS webhook_sub_active_idx RENAME TO webhook_sub_active_b2cf29_idx;
            
            -- Add provider_event_id index if not exists
            CREATE INDEX IF NOT EXISTS webhook_eve_provide_ef7be8_idx ON webhook_events(provider_event_id);
            """,
            reverse_sql="SELECT 1;"
        ),
    ]
