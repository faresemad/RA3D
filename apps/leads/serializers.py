from django.db import transaction
from rest_framework import serializers

from apps.leads.models import Leads, LeadsCategory, LeadsData
from apps.users.api.serializers.profile import UserProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadsCategory
        fields = "__all__"


class LeadsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadsCategory
        fields = ["id", "name"]


class LeadsSerializer(serializers.ModelSerializer):
    category = LeadsCategorySerializer()
    user = UserProfileSerializer()

    class Meta:
        model = Leads
        exclude = ["is_sold", "updated_at"]


class CreateLeadsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=LeadsCategory.objects.only("id", "name"))

    class Meta:
        model = Leads
        fields = "__all__"


class CreateLeadsDataSerializer(serializers.ModelSerializer):
    Leads = CreateLeadsSerializer()

    class Meta:
        model = LeadsData
        fields = "__all__"

    @transaction.atomic()
    def create(self, validated_data):
        leads_obj = validated_data.pop("leads")
        leads = Leads.objects.create(**leads_obj)
        leads_data = LeadsData.objects.create(leads=leads, **validated_data)
        return leads_data
