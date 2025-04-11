from rest_framework import serializers

from apps.sellers.models import SellerRequest


class SellerRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRequest
        fields = ["id", "national_id"]


class SellerRequestDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = SellerRequest
        fields = "__all__"
        read_only_fields = ["id", "user", "status", "created_at", "admin_comment"]


class SellerRequestAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRequest
        fields = ["status", "admin_comment"]
