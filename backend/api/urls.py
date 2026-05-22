from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, LogoutView, ProfileView, HouseholdViewSet, CategoryViewSet, PantryItemViewSet, RecipeViewSet, ItemLogViewSet, UserSearchView


router = DefaultRouter()
router.register(r'households', HouseholdViewSet, basename='household')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'pantry-items', PantryItemViewSet, basename='pantryitem')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'logs', ItemLogViewSet, basename='log')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/search-user/', UserSearchView.as_view(), name='search-user'),
    path('', include(router.urls)),
]
