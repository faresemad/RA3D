import logging

from django.contrib.auth import get_user_model
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.api.serializers.profile import ProfileSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class AccountViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer


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
