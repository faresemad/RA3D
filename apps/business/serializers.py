from django.db import transaction
from rest_framework import serializers

from apps.business.models import Business, BusinessCategory, BusinessData
from apps.users.api.serializers.profile import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = "__all__"


class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = ["id", "name"]


class BusinessSerializer(serializers.ModelSerializer):
    category = BusinessCategorySerializer()
    user = UserProfileSerializer()

    class Meta:
        model = Business
        exclude = ["is_sold", "updated_at"]


class CreateBusinessSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=BusinessCategory.objects.only("id", "name"))

    class Meta:
        model = Business
        fields = "__all__"


class CreateBusinessDataSerializer(serializers.ModelSerializer):
    business = CreateBusinessSerializer()

    class Meta:
        model = BusinessData
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        business_obj = validated_data.pop("business")
        business = Business.objects.create(**business_obj)
        business_data = BusinessData.objects.create(business=business, **validated_data)
        return business_data
