from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.users.models import CustomUserProfile

account_status = CustomUserProfile.AccountStatus


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="users:account-detail")
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ["id", "url", "email", "username", "first_name", "last_name", "picture", "status", "days_remaining"]
        read_only_fields = ["id", "email", "username", "status"]

    def get_days_remaining(self, obj: CustomUserProfile):
        if obj.status in [account_status.SUSPENDED, account_status.SELLER_SUSPENDED] and obj.is_lifelong_suspended:
            return "Lifetime"
        if obj.suspended_until:
            remaining_time = obj.suspended_until - timezone.now()
            return f"{remaining_time.days} days, {remaining_time.seconds // 3600} hours, {remaining_time.seconds // 60 % 60} minutes"  # noqa: E501
        return 0


class UnSuspendSerializer(serializers.Serializer):
    pass


class DURATION_UNIT:
    DAYS = "days"
    HOURS = "hours"
    MONTHS = "months"
    MINUTES = "minutes"


class SuspendSerializer(serializers.Serializer):
    duration_value = serializers.IntegerField(min_value=0, required=True)
    duration_unit = serializers.ChoiceField(
        choices=(
            (DURATION_UNIT.DAYS, "days"),
            (DURATION_UNIT.HOURS, "hours"),
            (DURATION_UNIT.MONTHS, "months"),
            (DURATION_UNIT.MINUTES, "minutes"),
        ),
        required=True,
    )
    reason = serializers.CharField(required=True)


class SuspendLifeTimeSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="users:account-detail")

    class Meta:
        model = CustomUserProfile
        fields = ["id", "username", "picture", "url"]


class UserInformationSuccessLoginSerializer(serializers.ModelSerializer):
    picture = serializers.SerializerMethodField()

    def get_picture(self, obj):
        if obj.picture:
            return self.context["request"].build_absolute_uri(obj.picture.url)
        return None

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "first_name", "last_name", "picture", "status"]
        read_only_fields = ["id", "email", "username", "status"]
