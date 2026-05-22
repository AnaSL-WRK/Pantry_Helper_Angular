from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Household, HouseholdMember, Category, PantryItem, Recipe, RecipeIngredient
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Load demo data for Pantry Helper'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        # Categories
        categories_data = [
            ('Dairy'), ('Meat'), ('Vegetables'), ('Fish'), ('Bakery'),
            ('Fruits'), ('Grains'), ('Drinks'), ('Pantry'),
            ('Condiments'), ('Frozen'), ('Snacks'),
        ]
        
        categories = {}
        for name in categories_data:
            cat, _ = Category.objects.get_or_create(name=name)
            categories[name] = cat

        # Users
        users = {}
        roles = [
            ('demo_admin', 'admin'),
            ('demo_manager', 'inventory_manager'),
            ('demo_member', 'member'),
            ('demo_viewer', 'viewer'),
        ]
        for username, role in roles:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com', 'first_name': username.replace('demo_', '').title()}
            )
            if created:
                user.set_password('demo1234')
                user.save()
            users[username] = (user, role)

        # Household
        admin_user = users['demo_admin'][0]
        household, _ = Household.objects.get_or_create(
            name='Demo Household',
            defaults={'description': 'A demo household for testing Pantry Helper', 'created_by': admin_user}
        )

        # Members
        for username, (user, role) in users.items():
            HouseholdMember.objects.get_or_create(
                household=household, user=user,
                defaults={'role': role}
            )

        today = date.today()

        # Pantry items
        items = [
            ('Milk', 'Dairy', 2, 'l', today + timedelta(days=5)),
            ('Cheddar Cheese', 'Dairy', 200, 'g', today + timedelta(days=14)),
            ('Chicken Breast', 'Meat', 500, 'g', today + timedelta(days=2)),
            ('Broccoli', 'Vegetables', 300, 'g', today + timedelta(days=4)),
            ('Carrots', 'Vegetables', 500, 'g', today + timedelta(days=10)),
            ('Tomatoes', 'Vegetables', 4, 'units', today + timedelta(days=6)),
            ('Onion', 'Vegetables', 3, 'units', today + timedelta(days=20)),
            ('Garlic', 'Vegetables', 1, 'units', today + timedelta(days=30)),
            ('Rice', 'Grains', 1, 'kg', today + timedelta(days=180)),
            ('Pasta', 'Grains', 500, 'g', today + timedelta(days=365)),
            ('Olive Oil', 'Condiments', 500, 'ml', today + timedelta(days=365)),
            ('Salt', 'Condiments', 500, 'g', None),
            ('Apple', 'Fruits', 5, 'units', today + timedelta(days=7)),
            ('Orange Juice', 'Beverages', 1, 'l', today + timedelta(days=8)),
            ('Eggs', 'Dairy', 12, 'units', today + timedelta(days=21)),
        ]

        for name, cat_name, qty, unit, expiry in items:
            PantryItem.objects.get_or_create(
                name=name, household=household,
                defaults={
                    'category': categories.get(cat_name),
                    'quantity': qty, 'unit': unit,
                    'expiry_date': expiry,
                    'status': 'available',
                    'added_by': admin_user
                }
            )

        # Recipes
        recipes_data = [
            {
                'name': 'Spaghetti Bolognese',
                'description': 'Classic Italian pasta dish',
                'instructions': '1. Cook pasta.\n2. Brown minced meat.\n3. Add tomatoes and onion.\n4. Mix with pasta.',
                'servings': 4,
                'prep_time_minutes': 30,
                'ingredients': [
                    ('Pasta', 400, 'g'), ('Tomatoes', 3, 'units'),
                    ('Onion', 1, 'units'), ('Garlic', 2, 'units'),
                    ('Olive Oil', 30, 'ml'),
                ]
            },
            {
                'name': 'Chicken Stir Fry',
                'description': 'Quick and healthy stir fry',
                'instructions': '1. Cut chicken.\n2. Stir fry with vegetables.\n3. Season and serve with rice.',
                'servings': 2,
                'prep_time_minutes': 20,
                'ingredients': [
                    ('Chicken Breast', 300, 'g'), ('Broccoli', 200, 'g'),
                    ('Carrots', 1, 'units'), ('Rice', 200, 'g'),
                    ('Olive Oil', 15, 'ml'),
                ]
            },
            {
                'name': 'Cheese Omelette',
                'description': 'Simple and delicious breakfast',
                'instructions': '1. Beat eggs.\n2. Cook in pan.\n3. Add cheese and fold.',
                'servings': 1,
                'prep_time_minutes': 10,
                'ingredients': [
                    ('Eggs', 3, 'units'), ('Cheddar Cheese', 50, 'g'),
                    ('Milk', 30, 'ml'),
                ]
            },
        ]

        for recipe_data in recipes_data:
            ingredients_data = recipe_data.pop('ingredients')
            recipe, created = Recipe.objects.get_or_create(
                name=recipe_data['name'],
                defaults={**recipe_data, 'created_by': admin_user, 'is_public': True}
            )
            if created:
                for ing_name, qty, unit in ingredients_data:
                    RecipeIngredient.objects.create(recipe=recipe, name=ing_name, quantity=qty, unit=unit)

        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))
        self.stdout.write('\nDemo accounts (password: demo1234):')
        self.stdout.write('  demo_admin     → Household Admin')
        self.stdout.write('  demo_manager   → Inventory Manager')
        self.stdout.write('  demo_member    → Member')
        self.stdout.write('  demo_viewer    → Viewer')
