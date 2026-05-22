from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Household, HouseholdMember, Category, PantryItem, Recipe, RecipeIngredient, ItemLog
from .serializers import (
    UserSerializer, HouseholdSerializer, HouseholdMemberSerializer,
    CategorySerializer, PantryItemSerializer, RecipeSerializer,
    ItemLogSerializer
)
from .permissions import get_user_role, has_min_role, ROLE_LEVELS


#auth
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#household
class HouseholdViewSet(viewsets.ModelViewSet):
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Household.objects.filter(members__user=self.request.user).distinct()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def update(self, request, *args, **kwargs):
        household = self.get_object()
        if not has_min_role(request.user, household, 'admin'):
            return Response({'error': 'Only admins can edit households.'}, status=403)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        household = self.get_object()
        if not has_min_role(request.user, household, 'admin'):
            return Response({'error': 'Only admins can edit households.'}, status=403)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        household = self.get_object()
        if not has_min_role(request.user, household, 'admin'):
            return Response({'error': 'Only admins can delete households.'}, status=403)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'post'])
    def members(self, request, pk=None):
        household = self.get_object()
        if request.method == 'GET':
            members = household.members.all()
            serializer = HouseholdMemberSerializer(members, many=True)
            return Response(serializer.data)

        if not has_min_role(request.user, household, 'admin'):
            return Response({'error': 'Only admins can manage members.'}, status=403)

        serializer = HouseholdMemberSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if HouseholdMember.objects.filter(household=household, user=user).exists():
                return Response({'error': 'User is already a member.'}, status=400)
            member = HouseholdMember.objects.create(
                household=household,
                user=user,
                role=serializer.validated_data.get('role', 'member')
            )
            return Response(HouseholdMemberSerializer(member).data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['patch', 'delete'], url_path='members/(?P<member_id>[^/.]+)')
    def manage_member(self, request, pk=None, member_id=None):
        household = self.get_object()
        if not has_min_role(request.user, household, 'admin'):
            return Response({'error': 'Only admins can manage members.'}, status=403)
        try:
            member = HouseholdMember.objects.get(id=member_id, household=household)
        except HouseholdMember.DoesNotExist:
            return Response({'error': 'Member not found.'}, status=404)

        if request.method == 'DELETE':
            member.delete()
            return Response(status=204)

        serializer = HouseholdMemberSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        household = self.get_object()
        items = PantryItem.objects.filter(household=household)
        today = timezone.now().date()
        expiring_soon = items.filter(
            expiry_date__lte=today + timedelta(days=7),
            expiry_date__gte=today,
            status='available'
        )
        return Response({
            'total_items': items.filter(status='available').count(),
            'expiring_soon': expiring_soon.count(),
            'expired': items.filter(expiry_date__lt=today, status='available').count(),
            'wasted': items.filter(status='wasted').count(),
            'consumed': items.filter(status='consumed').count(),
            'categories': items.filter(status='available').values('category__name').distinct().count(),
        })



#category
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]



#pantry item
class PantryItemViewSet(viewsets.ModelViewSet):
    serializer_class = PantryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'notes', 'category__name']
    ordering_fields = ['name', 'expiry_date', 'added_at', 'quantity']

    def get_queryset(self):
        user_households = Household.objects.filter(members__user=self.request.user)
        qs = PantryItem.objects.filter(household__in=user_households)

        household_id = self.request.query_params.get('household_id')
        if household_id:
            qs = qs.filter(household_id=household_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        category_id = self.request.query_params.get('category_id')
        if category_id:
            qs = qs.filter(category_id=category_id)

        expiring = self.request.query_params.get('expiring_soon')
        if expiring:
            today = timezone.now().date()
            qs = qs.filter(
                expiry_date__lte=today + timedelta(days=7),
                expiry_date__gte=today,
                status='available',
            ).order_by('expiry_date')

        expired_filter = self.request.query_params.get('expired')
        if expired_filter:
            today = timezone.now().date()
            qs = qs.filter(expiry_date__lt=today, status='available').order_by('expiry_date')

        return qs.select_related('category', 'added_by', 'household')

    def check_write_permission(self, household):
        return has_min_role(self.request.user, household, 'inventory_manager')

    def check_consume_permission(self, household):
        return has_min_role(self.request.user, household, 'member')

    def create(self, request, *args, **kwargs):
        household_id = request.data.get('household')
        try:
            household = Household.objects.get(id=household_id)
        except Household.DoesNotExist:
            return Response({'error': 'Household not found.'}, status=404)
        if not self.check_write_permission(household):
            return Response({'error': 'You need Inventory Manager role or above.'}, status=403)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        if not self.check_write_permission(item.household):
            return Response({'error': 'You need Inventory Manager role or above.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        if not self.check_write_permission(item.household):
            return Response({'error': 'You need Inventory Manager role or above.'}, status=403)
        ItemLog.objects.create(
            item_name=item.name,
            household=item.household,
            user=request.user,
            action='deleted',
            quantity_change=-item.quantity
        )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def consume(self, request, pk=None):
        item = self.get_object()
        if not self.check_consume_permission(item.household):
            return Response({'error': 'Permission denied.'}, status=403)
        quantity = float(request.data.get('quantity', item.quantity))
        if quantity <= 0:
            return Response({'error': 'Quantity must be greater than 0.'}, status=400)
        if quantity > item.quantity:
            return Response({'error': f'Cannot consume more than available ({item.quantity} {item.unit}).'}, status=400)
        item.quantity = round(item.quantity - quantity, 6)
        if item.quantity == 0:
            item.status = 'consumed'
        item.save()
        ItemLog.objects.create(
            item_name=item.name, household=item.household, user=request.user,
            action='consumed', quantity_change=-quantity
        )
        return Response(PantryItemSerializer(item, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def waste(self, request, pk=None):
        item = self.get_object()
        if not self.check_consume_permission(item.household):
            return Response({'error': 'Permission denied.'}, status=403)
        quantity = float(request.data.get('quantity', item.quantity))
        if quantity <= 0:
            return Response({'error': 'Quantity must be greater than 0.'}, status=400)
        if quantity > item.quantity:
            return Response({'error': f'Cannot waste more than available ({item.quantity} {item.unit}).'}, status=400)
        item.quantity = round(item.quantity - quantity, 6)
        if item.quantity == 0:
            item.status = 'wasted'
        item.save()
        ItemLog.objects.create(
            item_name=item.name, household=item.household, user=request.user,
            action='wasted', quantity_change=-quantity
        )
        return Response(PantryItemSerializer(item, context={'request': request}).data)




class RecipePagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000


#recipe
class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RecipePagination

    def check_recipe_write_permission(self, recipe):
        if recipe.is_preloaded:
            return False
        if recipe.created_by == self.request.user:
            return True
        return HouseholdMember.objects.filter(
            user=self.request.user,
            role='admin'
        ).exists()

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        if not self.check_recipe_write_permission(recipe):
            return Response({'error': 'You can only edit your own recipes.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if not self.check_recipe_write_permission(recipe):
            return Response({'error': 'You can only delete your own recipes.'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        qs = Recipe.objects.filter(
            Q(is_public=True) | Q(created_by=self.request.user)
        ).prefetch_related('ingredients')

        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(id__in=RecipeIngredient.objects.filter(name__icontains=search).values('recipe_id'))
            )

        household_id = self.request.query_params.get('household_id')
        if household_id:
            self.household_id = household_id
        return qs.distinct()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        household_id = self.request.query_params.get('household_id')
        if household_id:
            ctx['household_id'] = household_id
        return ctx

    @action(detail=False, methods=['get'])
    def suggested(self, request):
        household_id = request.query_params.get('household_id')
        if not household_id:
            return Response({'error': 'household_id required'}, status=400)

        pantry_items = PantryItem.objects.filter(
            household_id=household_id, status='available'
        )
        pantry_names = set(item.name.lower() for item in pantry_items)

        recipes = Recipe.objects.filter(
            Q(is_public=True) | Q(created_by=request.user)
        ).prefetch_related('ingredients')

        scored = []
        for recipe in recipes:
            ingredients = list(recipe.ingredients.all())
            if not ingredients:
                continue
            matched = sum(1 for i in ingredients if i.name.lower() in pantry_names)
            missing = len(ingredients) - matched
            if matched > 0:
                scored.append((missing, recipe))

        scored.sort(key=lambda x: x[0])
        top_recipes = [r for _, r in scored[:10]]
        serializer = RecipeSerializer(
            top_recipes, many=True,
            context={'request': request, 'household_id': household_id}
        )
        return Response(serializer.data)


#user search
 
class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        username = request.query_params.get('username', '').strip()
        if not username:
            return Response({'error': 'username parameter required'}, status=400)
        try:
            user = User.objects.get(username=username)
            return Response({'id': user.id, 'username': user.username,
                             'first_name': user.first_name, 'last_name': user.last_name})
        except User.DoesNotExist:
            return Response({'error': f'User "{username}" not found.'}, status=404)

#log
class ItemLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ItemLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_households = Household.objects.filter(members__user=self.request.user)
        qs = ItemLog.objects.filter(household__in=user_households).order_by('-timestamp')
        household_id = self.request.query_params.get('household_id')
        if household_id:
            qs = qs.filter(household_id=household_id)
        return qs
