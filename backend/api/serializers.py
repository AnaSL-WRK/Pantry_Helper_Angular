from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Household, HouseholdMember, Category, PantryItem, Recipe, RecipeIngredient, ItemLog
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class HouseholdMemberSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = HouseholdMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']


class HouseholdSerializer(serializers.ModelSerializer):
    members = HouseholdMemberSerializer(many=True, read_only=True)
    created_by = UserPublicSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    current_user_role = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'members', 'member_count', 'current_user_role']
        read_only_fields = ['created_by', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_current_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            member = obj.members.filter(user=request.user).first()
            return member.role if member else None
        return None

    def create(self, validated_data):
        user = self.context['request'].user
        household = Household.objects.create(created_by=user, **validated_data)
        HouseholdMember.objects.create(household=household, user=user, role='admin')
        return household


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class PantryItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, allow_null=True, required=False
    )
    added_by = UserPublicSerializer(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = PantryItem
        fields = [
            'id', 'household', 'name', 'category', 'category_id',
            'quantity', 'unit', 'expiry_date', 'status', 'notes',
            'added_by', 'added_at', 'updated_at', 'is_expired', 'days_until_expiry'
        ]
        read_only_fields = ['added_by', 'added_at', 'updated_at']

    def get_days_until_expiry(self, obj):
        if obj.expiry_date:
            delta = obj.expiry_date - timezone.now().date()
            return delta.days
        return None

    def create(self, validated_data):
        user = self.context['request'].user
        item = PantryItem.objects.create(added_by=user, **validated_data)
        ItemLog.objects.create(
            item_name=item.name,
            household=item.household,
            user=user,
            action='added',
            quantity_change=item.quantity
        )
        return item

    def update(self, instance, validated_data):
        user = self.context['request'].user
        old_quantity = instance.quantity
        item = super().update(instance, validated_data)
        action = 'updated'
        if item.status == 'consumed':
            action = 'consumed'
        elif item.status == 'wasted':
            action = 'wasted'
        ItemLog.objects.create(
            item_name=item.name,
            household=item.household,
            user=user,
            action=action,
            quantity_change=item.quantity - old_quantity
        )
        return item


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'quantity', 'unit']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    created_by = UserPublicSerializer(read_only=True)
    can_make = serializers.SerializerMethodField()
    missing_ingredients_count = serializers.SerializerMethodField()
    available_ingredient_names = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'instructions', 'servings',
                  'prep_time_minutes', 'created_by', 'is_public', 'is_preloaded', 'created_at',
                  'ingredients', 'can_make', 'missing_ingredients_count', 'available_ingredient_names']
        read_only_fields = ['created_by', 'created_at', 'is_preloaded']

    def _get_pantry_map(self, household_id):
        cache_key = f'_pantry_map_{household_id}'
        if cache_key not in self.context:
            pantry_items = PantryItem.objects.filter(
                household_id=household_id,
                status='available'
            )
            self.context[cache_key] = {item.name.lower(): item.quantity for item in pantry_items}
        return self.context[cache_key]

    def _get_household_id(self):
        request = self.context.get('request')
        return self.context.get('household_id') or (
            request.query_params.get('household_id') if request else None
        )

    def get_can_make(self, obj):
        household_id = self._get_household_id()
        if not household_id:
            return None
        pantry_map = self._get_pantry_map(household_id)
        if not pantry_map:  # no pantry items yet - don't evaluate
            return None
        ingredients = list(obj.ingredients.all())
        if not ingredients:
            return False
        return all(ing.name.lower() in pantry_map for ing in ingredients)

    def get_missing_ingredients_count(self, obj):
        household_id = self._get_household_id()
        if not household_id:
            return None
        pantry_map = self._get_pantry_map(household_id)
        if not pantry_map:  # no pantry items yet - don't evaluate
            return None
        return sum(1 for ing in obj.ingredients.all() if ing.name.lower() not in pantry_map)

    def get_available_ingredient_names(self, obj):
        household_id = self._get_household_id()
        if not household_id:
            return []
        pantry_map = self._get_pantry_map(household_id)
        return [ing.name.lower() for ing in obj.ingredients.all() if ing.name.lower() in pantry_map]

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(created_by=user, **validated_data)
        for ing_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ing_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        recipe = super().update(instance, validated_data)
        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for ing_data in ingredients_data:
                RecipeIngredient.objects.create(recipe=recipe, **ing_data)
        return recipe


class ItemLogSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = ItemLog
        fields = ['id', 'item_name', 'user', 'action', 'quantity_change', 'timestamp', 'notes']
