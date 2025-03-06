import logging
from decimal import Decimal

import pandas as pd
from rest_framework import serializers

from apps.users.api.serializers.profile import UserProfileSerializer
from apps.webmails.models import WebMail, WebMailCategory, WebMailNiche, WebMailStatus, WebMailType

logger = logging.getLogger(__name__)


class WebMailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = WebMail
        exclude = ["updated_at"]


class ListWebMailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = WebMail
        exclude = ["updated_at", "username", "password"]


class CreateWebMailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = WebMail
        exclude = ["status", "is_sold"]


class BulkCreateWebMailTextSerializer(serializers.Serializer):
    data = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Parse textarea input and validate each WebMail entry.
        Expected format:
        username | password | domain | price | source | category | niche
        """
        logger.info("Starting validation of bulk WebMail data")
        value = attrs.get("data", "").strip()
        lines = value.split("\n")
        webmails = []
        errors = []

        logger.debug(f"Processing {len(lines)} lines of WebMail data")
        for index, line in enumerate(lines, start=1):
            parts = line.split("|")
            if len(parts) != 7:
                logger.warning(f"Line {index} has incorrect number of columns: {len(parts)}")
                errors.append(f"Line {index}: Incorrect number of columns (Expected 7, got {len(parts)})")
                continue

            username, password, domain, price, source, category, niche = (p.strip() for p in parts)

            try:
                price = Decimal(price)
                if price < 1:
                    errors.append(f"Line {index}: Price must be at least 1")
            except ValueError:
                errors.append(f"Line {index}: Invalid price format")

            if source not in dict(WebMailType.choices):
                errors.append(f"Line {index}: Invalid source '{source}'")
            if category not in dict(WebMailCategory.choices):
                errors.append(f"Line {index}: Invalid category '{category}'")
            if niche not in dict(WebMailNiche.choices):
                errors.append(f"Line {index}: Invalid niche '{niche}'")

            if not errors:
                webmails.append(
                    {
                        "username": username,
                        "password": password,
                        "domain": domain,
                        "price": price,
                        "source": source,
                        "category": category,
                        "niche": niche,
                        "status": WebMailStatus.UNSOLD,  # Default status to UNSOLD
                        "is_sold": False,
                    }
                )

        if errors:
            raise serializers.ValidationError({"errors": errors})

        logger.info(f"Validation completed successfully. {len(webmails)} WebMails ready for creation")
        return {"webmails": webmails}

    def create(self, validated_data):
        """Bulk create WebMail records, skipping duplicates"""
        request_user = self.context["request"].user
        webmails_data = validated_data["webmails"]

        # Fetch existing WebMails for this user based on (username, domain)
        existing_webmails = set(WebMail.objects.filter(user=request_user).values_list("username", "domain"))

        # Filter out duplicate WebMails
        new_webmails = [
            WebMail(**data, user=request_user)
            for data in webmails_data
            if (data["username"], data["domain"]) not in existing_webmails
        ]

        if not new_webmails:
            return {
                "message": "No new WebMails were created. All provided WebMails already exist.",
                "created_count": 0,
            }

        created_webmails = WebMail.objects.bulk_create(new_webmails)

        return {
            "message": f"{len(created_webmails)} WebMails created successfully.",
            "created_count": len(created_webmails),
        }


class BulkUploadWebMailSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate(self, attrs):
        """Validate and parse the uploaded file."""
        file = attrs.get("file", None)
        if not file:
            raise serializers.ValidationError("No file uploaded.")

        file_extension = file.name.split(".")[-1].lower()

        if file_extension not in ["xlsx", "txt"]:
            raise serializers.ValidationError("Only .xlsx (Excel) and .txt files are supported.")

        webmails = []
        errors = []

        # Read XLSX File
        if file_extension == "xlsx":
            try:
                df = pd.read_excel(file)
            except Exception as e:
                raise serializers.ValidationError(f"Error reading Excel file: {str(e)}")

            expected_columns = ["username", "password", "domain", "price", "source", "category", "niche"]

            # Check if all required columns exist
            if not all(col in df.columns for col in expected_columns):
                raise serializers.ValidationError(f"Excel file must contain columns: {', '.join(expected_columns)}")

            # Parse each row
            for index, row in df.iterrows():
                try:
                    username = str(row["username"]).strip()
                    password = str(row["password"]).strip()
                    domain = str(row["domain"]).strip()
                    price = Decimal(row["price"])
                    source = str(row["source"]).strip()
                    category = str(row["category"]).strip()
                    niche = str(row["niche"]).strip()

                    if price < 1:
                        errors.append(f"Row {index + 2}: Price must be at least 1")
                    if source not in dict(WebMailType.choices):
                        errors.append(f"Row {index + 2}: Invalid source '{source}'")
                    if category not in dict(WebMailCategory.choices):
                        errors.append(f"Row {index + 2}: Invalid category '{category}'")
                    if niche not in dict(WebMailNiche.choices):
                        errors.append(f"Row {index + 2}: Invalid niche '{niche}'")

                    if not errors:
                        webmails.append(
                            {
                                "username": username,
                                "password": password,
                                "domain": domain,
                                "price": price,
                                "source": source,
                                "category": category,
                                "niche": niche,
                                "status": WebMailStatus.UNSOLD,
                                "is_sold": False,
                            }
                        )

                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

        # Read TXT File
        elif file_extension == "txt":
            try:
                content = file.read().decode("utf-8").strip()
                lines = content.split("\n")
            except Exception:
                raise serializers.ValidationError("Error reading TXT file. Ensure it's UTF-8 encoded.")

            for index, line in enumerate(lines, start=1):
                parts = line.split("|")
                if len(parts) != 7:
                    errors.append(f"Line {index}: Incorrect number of columns (Expected 7, got {len(parts)})")
                    continue

                username, password, domain, price, source, category, niche = (p.strip() for p in parts)

                try:
                    price = Decimal(price)
                    if price < 1:
                        errors.append(f"Line {index}: Price must be at least 1")
                except ValueError:
                    errors.append(f"Line {index}: Invalid price format")

                if source not in dict(WebMailType.choices):
                    errors.append(f"Line {index}: Invalid source '{source}'")
                if category not in dict(WebMailCategory.choices):
                    errors.append(f"Line {index}: Invalid category '{category}'")
                if niche not in dict(WebMailNiche.choices):
                    errors.append(f"Line {index}: Invalid niche '{niche}'")

                if not errors:
                    webmails.append(
                        {
                            "username": username,
                            "password": password,
                            "domain": domain,
                            "price": price,
                            "source": source,
                            "category": category,
                            "niche": niche,
                            "status": WebMailStatus.UNSOLD,
                            "is_sold": False,
                        }
                    )

        if errors:
            raise serializers.ValidationError({"errors": errors})

        attrs["webmails"] = webmails
        return attrs

    def create(self, validated_data):
        """Bulk create WebMail records, skipping duplicates"""
        request_user = self.context["request"].user
        webmails_data = validated_data["webmails"]

        existing_webmails = set(WebMail.objects.filter(user=request_user).values_list("username", "domain"))

        new_webmails = [
            WebMail(**data, user=request_user)
            for data in webmails_data
            if (data["username"], data["domain"]) not in existing_webmails
        ]

        created_webmails = WebMail.objects.bulk_create(new_webmails)

        return {
            "message": f"{len(created_webmails)} WebMails created successfully.",
            "created_count": len(created_webmails),
        }
