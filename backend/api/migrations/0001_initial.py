from django.conf import settings
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.CreateModel(
            name='Household',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_households', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('instructions', models.TextField()),
                ('servings', models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1)])),
                ('prep_time_minutes', models.IntegerField(default=30, validators=[django.core.validators.MinValueValidator(0)])),
                ('is_public', models.BooleanField(default=True)),
                ('is_preloaded', models.BooleanField(default=False)),
                ('source_url', models.URLField(blank=True, default='')),
                ('source_site', models.CharField(blank=True, default='', max_length=100)),
                ('author', models.CharField(blank=True, default='', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HouseholdMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('viewer', 'Viewer'), ('member', 'Member'), ('inventory_manager', 'Inventory Manager'), ('admin', 'Household Admin')], default='member', max_length=20)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='api.household')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='household_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('household', 'user')}},
        ),
        migrations.CreateModel(
            name='PantryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('unit', models.CharField(choices=[('g', 'Grams'), ('kg', 'Kilograms'), ('ml', 'Milliliters'), ('l', 'Liters'), ('units', 'Units'), ('tbsp', 'Tablespoon'), ('tsp', 'Teaspoon'), ('cup', 'Cup')], default='units', max_length=10)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('available', 'Available'), ('low', 'Low Stock'), ('consumed', 'Consumed'), ('wasted', 'Wasted')], default='available', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_items', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.category')),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pantry_items', to='api.household')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('quantity', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('unit', models.CharField(default='units', max_length=20)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='api.recipe')),
            ],
        ),
        migrations.CreateModel(
            name='ItemLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('action', models.CharField(choices=[('added', 'Added'), ('updated', 'Updated'), ('consumed', 'Consumed'), ('wasted', 'Wasted'), ('deleted', 'Deleted')], max_length=20)),
                ('quantity_change', models.FloatField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='api.household')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
