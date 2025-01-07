import uuid

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

User = get_user_model()


class BusinessCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class BusinessData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.FileField(
        upload_to="secret/business/data/",
        validators=[FileExtensionValidator(allowed_extensions=["txt", "pdf", "docx"])],
    )
    business = models.OneToOneField("Business", on_delete=models.CASCADE, related_name="secret_data")

    def __str__(self):
        return self.data.name


class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(BusinessCategory, on_delete=models.CASCADE, related_name="business")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business")
    location = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    website_domain = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=255)
    niche = models.CharField(max_length=255)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.website_domain

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "category"]),
        ]

    def mark_as_sold(self):
        self.is_sold = True
        self.save()
