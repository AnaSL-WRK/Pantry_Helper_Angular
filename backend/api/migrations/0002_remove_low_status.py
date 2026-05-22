from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE api_pantryitem SET status = 'available' WHERE status = 'low';",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='pantryitem',
            name='status',
            field=models.CharField(
                choices=[
                    ('available', 'Available'),
                    ('consumed', 'Consumed'),
                    ('wasted', 'Wasted'),
                ],
                default='available',
                max_length=20,
            ),
        ),
    ]
