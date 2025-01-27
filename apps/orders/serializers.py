from rest_framework import serializers

from apps.accounts.models import Account
from apps.cpanel.models import CPanel
from apps.orders.models import Order, OrderStatus, PaymentMethod
from apps.rdp.models import Rdp
from apps.shells.models import Shell


class CreateOrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)
    cpanel = serializers.PrimaryKeyRelatedField(queryset=CPanel.objects.all(), required=False)
    rdp = serializers.PrimaryKeyRelatedField(queryset=Rdp.objects.all(), required=False)
    shell = serializers.PrimaryKeyRelatedField(queryset=Shell.objects.all(), required=False)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["id", "user", "total_price", "created_at", "updated_at"]
        extra_kwargs = {
            "status": {"default": OrderStatus.PENDING},
            "payment_method": {"default": PaymentMethod.CRYPTO},
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Order.objects.all(),
                fields=["user", "account", "cpanel", "rdp", "shell"],
                message="You can only have one order per account, cpanel, rdp, and shell.",
            )
        ]

    def validate(self, attrs):
        if not any(attrs.values()):
            raise serializers.ValidationError("At least one of account, cpanel, rdp, or shell must be provided.")
        return attrs
