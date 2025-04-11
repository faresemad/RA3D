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


class ListSellerRequestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    status = serializers.ChoiceField(choices=SellerRequest.Status.choices)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    admin_comment = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = SellerRequest
        fields = "__all__"
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]
