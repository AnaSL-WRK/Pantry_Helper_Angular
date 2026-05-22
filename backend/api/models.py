from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Household(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_households')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HouseholdMember(models.Model):
    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('member', 'Member'),
        ('inventory_manager', 'Inventory Manager'),
        ('admin', 'Household Admin'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='household_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('household', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.household.name} ({self.role})"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class PantryItem(models.Model):
    UNIT_CHOICES = [
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
        ('units', 'Units'),
        ('tbsp', 'Tablespoon'),
        ('tsp', 'Teaspoon'),
        ('cup', 'Cup'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('consumed', 'Consumed'),
        ('wasted', 'Wasted'),
    ]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='pantry_items')
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='units')
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    notes = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_items')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.household.name})"

    @property
    def is_expired(self):
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField()
    servings = models.IntegerField(default=2, validators=[MinValueValidator(1)])
    prep_time_minutes = models.IntegerField(default=30, validators=[MinValueValidator(0)])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_preloaded = models.BooleanField(default=False)
    source_url = models.URLField(blank=True, default='')
    source_site = models.CharField(max_length=100, blank=True, default='')
    author = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=100)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, default='units')

    def __str__(self):
        return f"{self.name} for {self.recipe.name}"


class ItemLog(models.Model):
    ACTION_CHOICES = [
        ('added', 'Added'),
        ('updated', 'Updated'),
        ('consumed', 'Consumed'),
        ('wasted', 'Wasted'),
        ('deleted', 'Deleted'),
    ]
    
    item_name = models.CharField(max_length=100)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_change = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} - {self.item_name} ({self.timestamp})"
