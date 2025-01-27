import logging

from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.users.api.serializers.profile import (
    DURATION_UNIT,
    ProfileSerializer,
    SuspendLifeTimeSerializer,
    SuspendSerializer,
    UnSuspendSerializer,
)
from apps.users.models import CustomUserProfile

User: CustomUserProfile = get_user_model()
logger = logging.getLogger(__name__)


class AccountViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_serializer_class(self):
        if self.action == "unsuspend":
            return UnSuspendSerializer
        elif self.action == "suspend":
            return SuspendSerializer
        elif self.action == "suspend_lifetime":
            return SuspendLifeTimeSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ["suspend", "unsuspend"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        logger.info(f"Suspending user with pk: {pk}")
        user: CustomUserProfile = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        duration_value = serializer.validated_data["duration_value"]
        duration_unit = serializer.validated_data["duration_unit"]
        reason = serializer.validated_data["reason"]

        # Convert duration to days
        if duration_unit == DURATION_UNIT.DAYS:
            duration_days = duration_value
        elif duration_unit == DURATION_UNIT.HOURS:
            duration_days = duration_value / 24  # Convert hours to days
        elif duration_unit == DURATION_UNIT.MONTHS:
            duration_days = duration_value * 30  # Approximate months to days
        elif duration_unit == DURATION_UNIT.MINUTES:
            duration_days = duration_value / 1440  # Approximate minutes to days

        user.suspend(duration_days=duration_days, reason=reason)

        logger.info(f"User  {user.username} suspended until {user.suspended_until} for reason: {reason}")
        logger.debug("Notification sent to suspended user")
        return Response({"status": "Account suspended"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def suspend_lifetime(self, request, pk=None):
        logger.info(f"Suspending user with pk: {pk} for lifetime")
        user: CustomUserProfile = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data["reason"]
        user.suspend_lifetime(reason=reason)
        logger.info(f"User {user.username} suspended for lifetime")
        logger.debug("Notification sent to suspended user")
        return Response({"status": "Account suspended for lifetime"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def unsuspend(self, request, pk=None):
        logger.info(f"Unsuspending user with pk: {pk}")
        user: CustomUserProfile = self.get_object()
        user.unsuspend()
        logger.info(f"User {user.username} unsuspended")
        logger.debug("Notification sent to unsuspended user")
        return Response({"status": "Account unsuspended"}, status=status.HTTP_200_OK)


class ProfileViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "patch"]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        user = self.get_object()

        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(user, data=request.data, partial=(request.method == "PATCH"))
        if serializer.is_valid():
            logger.debug("Serializer is valid, saving user data")
            serializer.save()
            return Response(serializer.data)
        logger.warning(f"Serializer validation failed : {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
