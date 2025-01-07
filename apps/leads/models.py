import uuid

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

User = get_user_model()


class LeadsCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LeadsData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data = models.FileField(
        upload_to="secret/leads/data/",
        validators=[FileExtensionValidator(allowed_extensions=["txt", "pdf", "docx"])],
    )
    leads = models.OneToOneField("Leads", on_delete=models.CASCADE, related_name="secret_data")

    def __str__(self):
        return self.data.name


class Leads(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(LeadsCategory, on_delete=models.CASCADE, related_name="leads")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads")
    location = models.CharField(max_length=255)
    description = models.TextField()
    niche = models.CharField(max_length=255)
    website_domain = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    emails_number = models.IntegerField()
    proof = models.FileField(upload_to="leads/proofs/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
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
