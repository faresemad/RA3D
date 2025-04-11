from rest_framework import serializers

from apps.accounts.models import Account
from apps.cpanel.models import CPanel
from apps.rdp.models import Rdp
from apps.shells.models import Shell
from apps.smtp.models import SMTP
from apps.webmails.models import WebMail


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "domain"]


class CPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPanel
        fields = ["id", "host"]


class RdpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rdp
        fields = ["id", "ip"]


class ShellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shell
        fields = ["id", "shell_url"]


class SMTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTP
        fields = ["id", "ip"]


class WebMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebMail
        fields = ["id", "domain"]


class SecretAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ["user"]


class SecretCPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPanel
        exclude = ["user"]


class SecretRdpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rdp
        exclude = ["user"]


class SecretShellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shell
        exclude = ["user"]


class SecretSMTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTP
        exclude = ["user"]


class SecretWebMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebMail
        exclude = ["user"]
