import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, URLValidator
from django.db import models

User = get_user_model()


class AccountCategory(models.TextChoices):
    EMAIL_MARKETING = "email_marketing", "Email Marketing"
    WEBMAIL_BUSINESS = "webmail_business", "Webmail Business"
    MARKETING_TOOLS = "marketing_tools", "Marketing Tools"
    HOSTING_DOMAIN = "hosting_domain", "Hosting Domain"
    GAMES = "games", "Games"
    GRAPHIC_DEVELOPER = "graphic_developer", "Graphic Developer"
    VPN_SOCKS_PROXY = "vpn_socks_proxy", "VPN Socks Proxy"
    SHOPPING = "shopping", "Shopping"
    PROGRAM = "program", "Program"
    STREAM = "stream", "Stream"
    DATING = "dating", "Dating"
    LEARNING = "learning", "Learning"
    TORENT = "torent", "Torent"
    VOIP = "voip", "VOIP"
    OTHER = "other", "Other"


class AccountType(models.TextChoices):
    CREATED = "created", "Craeted"
    HACKED = "hacked", "Hacked / Cracked"


class AccountStatus(models.TextChoices):
    SOLD = "sold", "Sold"
    UNSOLD = "unsold", "Un Sold"
    DELETED = "deleted", "Deleted"


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    domain = models.URLField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    category = models.CharField(max_length=255, choices=AccountCategory.choices, default=AccountCategory.OTHER)
    country = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=AccountType.choices, default=AccountType.CREATED)
    details = models.TextField()
    notes = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    proof = models.URLField(validators=[URLValidator(regex=r"^https?:\/\/((?:vgy\.me|prnt\.sc|gyazo\.com)\/.*)")])
    status = models.CharField(max_length=255, choices=AccountStatus.choices, default=AccountStatus.UNSOLD)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.category} - {self.price}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "category"]),
        ]

    def mark_as_sold(self):
        self.status = AccountStatus.SOLD
        self.is_sold = True
        self.save()

    def mark_as_unsold(self):
        self.status = AccountStatus.UNSOLD
        self.is_sold = False
        self.save()

    def mark_as_deleted(self):
        self.status = AccountStatus.DELETED
        self.save()
