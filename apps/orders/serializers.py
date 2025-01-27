from rest_framework import serializers

from apps.orders.helper.serializers import AccountSerializer, CPanelSerializer, RdpSerializer, ShellSerializer
from apps.orders.models import Order, PaymentMethod


class CreateOrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["id", "user", "total_price", "status", "created_at", "updated_at"]
        extra_kwargs = {
            "payment_method": {"default": PaymentMethod.CRYPTO},
        }

    def validate(self, attrs):
        products = [attrs.get("account"), attrs.get("cpanel"), attrs.get("rdp"), attrs.get("shell")]
        selected_products = sum(1 for product in products if product)

        if selected_products == 0:
            raise serializers.ValidationError("You must select one product (account, cpanel, rdp, or shell).")
        if selected_products > 1:
            raise serializers.ValidationError("You can only select one product at a time.")

        return attrs


class ListOrderSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    cpanel = CPanelSerializer()
    rdp = RdpSerializer()
    shell = ShellSerializer()

    class Meta:
        model = Order
        fields = ["id", "account", "cpanel", "rdp", "shell", "total_price", "status", "payment_method", "created_at"]
