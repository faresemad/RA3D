import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class WebMailCategory(models.TextChoices):
    CPANEL = "cPanel Webmail", "cPanel Webmail"
    GODADDY = "GoDaddy Webmail", "GoDaddy Webmail"
    OFFICE365 = "Office 365", "Office 365"
    GSUITE = "Google Workspace", "Google Workspace"
    ZOHO = "Zoho Mail", "Zoho Mail"
    RACKSPACE = "Rackspace Email", "Rackspace Email"
    IONOS = "IONOS Webmail", "IONOS Webmail"


class WebMailType(models.TextChoices):
    CREATED = "Created", "Created"
    HACKED = "Hacked / Cracked", "Hacked / Cracked"
    LOGS = "Logs", "Logs"


class WebMailStatus(models.TextChoices):
    SOLD = "Sold", "Sold"
    UNSOLD = "Unsold", "Unsold"
    DELETED = "Deleted", "Deleted"


class WebMailNiche(models.TextChoices):
    REAL_STATE = "Real State", "Real State"
    HEALTH_FITNESS = "Health - Fitness", "Health - Fitness"
    HOBBIES_INTEREST = "Hobbies - Interest", "Hobbies - Interest"
    RELATIONSHIP_DATING = "Relationship - Dating", "Relationship - Dating"
    WEALTH_MONEY = "Wealth - Money", "Wealth - Money"
    EDUCATION = "Education", "Education"
    PREPPING = "Prepping", "Prepping"
    SELF_IMPROVEMENT = "Self-Improvement", "Self-Improvement"
    WEALTH_BUILDING = "Wealth Building Through Investing", "Wealth Building Through Investing"
    PETS = "Pets", "Pets"
    BEAUTY = "Beauty", "Beauty"
    GADGETS_TECHNOLOGY = "Gadgets - Technology", "Gadgets - Technology"
    PERSONAL_FINANCE = "Personal Finance", "Personal Finance"
    HOME_SECURITY = "Home Security", "Home Security"
    BABIES = "Babies", "Babies"
    OTHER = "Other", "Other"


class WebMail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="webmail")
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    domain = models.URLField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    source = models.CharField(max_length=255, choices=WebMailType.choices, default=WebMailType.CREATED)
    category = models.CharField(max_length=255, choices=WebMailCategory.choices, default=WebMailCategory.CPANEL)
    niche = models.CharField(max_length=255, choices=WebMailNiche.choices, default=WebMailNiche.OTHER)
    status = models.CharField(max_length=255, choices=WebMailStatus.choices, default=WebMailStatus.UNSOLD)
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
        self.status = WebMailStatus.SOLD
        self.is_sold = True
        self.save()

    def mark_as_deleted(self):
        self.status = WebMailStatus.DELETED
        self.save()
