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
