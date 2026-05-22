from django.contrib import admin
from .models import Household, HouseholdMember, Category, PantryItem, Recipe, RecipeIngredient, ItemLog

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']

@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'household', 'role', 'joined_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'household', 'quantity', 'unit', 'status', 'expiry_date']
    list_filter = ['status', 'category']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'servings', 'prep_time_minutes', 'is_public']

admin.site.register(RecipeIngredient)
admin.site.register(ItemLog)
