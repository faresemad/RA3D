from rest_framework.permissions import BasePermission

from apps.users.models import CustomUserProfile


class BaseStatusPermission(BasePermission):
    """
    Base permission to check if the user's status matches a specific account status.
    """

    required_status = None

    def has_permission(self, request, view):
        # Ensure user is authenticated and has the required status
        return request.user.is_authenticated and getattr(request.user, "status", None) == self.required_status


class IsSeller(BaseStatusPermission):
    """
    Permission for users with the SELLER account status.
    """

    required_status = CustomUserProfile.AccountStatus.SELLER or CustomUserProfile.AccountStatus.ADMIN


class IsBuyer(BaseStatusPermission):
    """
    Permission for users with the BUYER account status.
    """

    required_status = CustomUserProfile.AccountStatus.BUYER


class IsSupport(BaseStatusPermission):
    """
    Permission for users with the SUPPORT account status.
    """

    required_status = CustomUserProfile.AccountStatus.SUPPORT or CustomUserProfile.AccountStatus.ADMIN


class IsOwnerOrAdmin(BasePermission):
    """
    Permission to check if the request user is the object owner or an admin.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (obj.user == request.user or request.user.is_staff)


class IsOwner(BasePermission):
    """
    Permission to check if the request user is the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.user == request.user


class IsAccountAdmin(BaseStatusPermission):
    """
    Permission for users with the ADMIN account status.
    """

    required_status = CustomUserProfile.AccountStatus.ADMIN


class IsAccountModerator(BaseStatusPermission):
    """
    Permission for users with the Moderator account status.
    """

    required_status = CustomUserProfile.AccountStatus.MODERATOR
