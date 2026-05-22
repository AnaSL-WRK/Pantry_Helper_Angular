from rest_framework.permissions import BasePermission
from .models import HouseholdMember

ROLE_LEVELS = {
    'viewer': 1,
    'member': 2,
    'inventory_manager': 3,
    'admin': 4,
}


def get_user_role(user, household):
    try:
        member = HouseholdMember.objects.get(user=user, household=household)
        return member.role
    except HouseholdMember.DoesNotExist:
        return None


def has_min_role(user, household, min_role):
    role = get_user_role(user, household)
    if role is None:
        return False
    return ROLE_LEVELS.get(role, 0) >= ROLE_LEVELS.get(min_role, 0)


#allow any member of the household (1,2,3,4)
class IsHouseholdMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        household = getattr(obj, 'household', obj)
        return get_user_role(request.user, household) is not None


#allow inventory managers and household admins (3,4)
class IsInventoryManagerOrAbove(BasePermission):
    message = "You need at least Inventory Manager role."

    def has_object_permission(self, request, view, obj):
        household = getattr(obj, 'household', obj)
        return has_min_role(request.user, household, 'inventory_manager')


#allow only household admins (4)
class IsHouseholdAdmin(BasePermission):
    message = "You need to be a Household Admin."

    def has_object_permission(self, request, view, obj):
        household = getattr(obj, 'household', obj)
        return has_min_role(request.user, household, 'admin')
