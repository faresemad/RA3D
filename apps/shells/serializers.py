import logging
from decimal import Decimal

import pandas as pd
from django.db import IntegrityError
from django.db.models.signals import post_save
from rest_framework import serializers

from apps.shells.models import Shell, ShellStatus, ShellType
from apps.users.api.serializers.profile import UserProfileSerializer

logger = logging.getLogger(__name__)


class ShellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shell
        fields = [
            "id",
            "shell_url",
            "shell_type",
            "status",
            "price",
            "ssl",
            "tld",
            "details",
            "created_at",
            "is_deleted",
        ]


class ShellListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Shell
        fields = [
            "id",
            "user",
            "shell_type",
            "status",
            "price",
            "ssl",
            "tld",
            "details",
            "created_at",
        ]


class CreateShellSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Shell
        fields = [
            "id",
            "user",
            "shell_url",
            "shell_type",
            "price",
        ]


class BulkCreateShellTextSerializer(serializers.Serializer):
    data = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Parse textarea input and validate each Shell entry.
        Expected format:
        shell_url | shell_type | price
        """
        logger.info("Starting validation of bulk Shell data")
        value = attrs.get("data", "").strip()
        lines = value.split("\n")
        shells = []
        errors = []

        logger.debug(f"Processing {len(lines)} lines of Shell data")
        for index, line in enumerate(lines, start=1):
            parts = line.split("|")
            if len(parts) != 3:
                logger.warning(f"Line {index} has incorrect number of columns: {len(parts)}")
                errors.append(f"Line {index}: Incorrect number of columns (Expected 3, got {len(parts)})")
                continue

            shell_url, shell_type, price = (p.strip() for p in parts)

            try:
                price = Decimal(price)
                if price < 1:
                    logger.warning(f"Line {index} has invalid price: {price}")
                    errors.append(f"Line {index}: Price must be at least 1")
            except ValueError:
                logger.warning(f"Line {index} has invalid price format: {price}")
                errors.append(f"Line {index}: Invalid price format")

            if shell_type not in dict(ShellType.choices):
                logger.warning(f"Line {index} has invalid Shell type: {shell_type}")
                errors.append(f"Line {index}: Invalid Shell type '{shell_type}'")

            if not errors:
                logger.debug(f"Line {index} validated successfully")
                shells.append(
                    {
                        "shell_url": shell_url,
                        "shell_type": shell_type,
                        "price": price,
                        "status": ShellStatus.UNSOLD,  # Default to UNSOLD
                        "ssl": False,
                        "tld": None,
                        "details": {},
                    }
                )

        if errors:
            logger.error(f"Validation failed with {len(errors)} errors")
            raise serializers.ValidationError({"errors": errors})

        logger.info(f"Validation completed successfully. {len(shells)} Shells ready for creation")
        return {"shells": shells}

    def create(self, validated_data):
        """Bulk create Shell records"""
        logger.info("Starting bulk creation of Shells")
        request_user = self.context["request"].user
        shells_data = validated_data["shells"]

        for shell_data in shells_data:
            shell_data["user"] = request_user

        # Fetch existing Shell URLs for this user
        existing_shells = set(Shell.objects.filter(user=request_user).values_list("shell_url", flat=True))

        # Filter out duplicate shell URLs
        new_shells = [Shell(**data) for data in shells_data if data["shell_url"] not in existing_shells]

        if not new_shells:
            return {"message": b"No new Shells were created. All provided Shells already exist.", b"created_count": 0}

        try:
            created_shells = Shell.objects.bulk_create(new_shells)
            for instance in created_shells:
                post_save.send(sender=Shell, instance=instance, created=True)
            return created_shells
        except IntegrityError:
            raise serializers.ValidationError("Duplicate shell entries detected in the file.")


class BulkUploadShellSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate(self, attrs):
        """Validate and parse the uploaded file."""
        file = attrs.get("file", None)
        if not file:
            raise serializers.ValidationError("No file uploaded.")

        file_extension = file.name.split(".")[-1].lower()

        if file_extension not in ["xlsx", "txt"]:
            raise serializers.ValidationError("Only .xlsx (Excel) and .txt files are supported.")

        shells = []
        errors = []

        # Read XLSX File
        if file_extension == "xlsx":
            try:
                df = pd.read_excel(file)
            except Exception as e:
                raise serializers.ValidationError(f"Error reading Excel file: {str(e)}")

            expected_columns = ["shell_url", "shell_type", "price"]

            # Check if all required columns exist
            if not all(col in df.columns for col in expected_columns):
                raise serializers.ValidationError(f"Excel file must contain columns: {', '.join(expected_columns)}")

            # Parse each row
            for index, row in df.iterrows():
                try:
                    shell_url = str(row["shell_url"]).strip()
                    shell_type = str(row["shell_type"]).strip()
                    price = Decimal(row["price"])

                    if price < 1:
                        errors.append(f"Row {index + 2}: Price must be at least 1")

                    if shell_type not in dict(ShellType.choices):
                        errors.append(f"Row {index + 2}: Invalid Shell type '{shell_type}'")

                    if not errors:
                        shells.append(
                            {
                                "shell_url": shell_url,
                                "shell_type": shell_type,
                                "price": price,
                                "status": ShellStatus.UNSOLD,
                                "ssl": False,
                                "tld": None,
                                "details": {},
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
                if len(parts) != 3:
                    errors.append(f"Line {index}: Incorrect number of columns (Expected 3, got {len(parts)})")
                    continue

                shell_url, shell_type, price = (p.strip() for p in parts)

                try:
                    price = Decimal(price)
                    if price < 1:
                        errors.append(f"Line {index}: Price must be at least 1")
                except ValueError:
                    errors.append(f"Line {index}: Invalid price format")

                if shell_type not in dict(ShellType.choices):
                    errors.append(f"Line {index}: Invalid Shell type '{shell_type}'")

                if not errors:
                    shells.append(
                        {
                            "shell_url": shell_url,
                            "shell_type": shell_type,
                            "price": price,
                            "status": ShellStatus.UNSOLD,
                            "ssl": False,
                            "tld": None,
                            "details": {},
                        }
                    )

        if errors:
            raise serializers.ValidationError({"errors": errors})

        attrs["shells"] = shells  # ✅ Ensure 'shells' key exists
        return attrs

    def create(self, validated_data):
        """Bulk create Shell records"""
        logger.info("Starting bulk creation of Shells")
        request_user = self.context["request"].user
        shells_data = validated_data["shells"]

        for shell_data in shells_data:
            shell_data["user"] = request_user

        # Fetch existing Shell URLs for this user
        existing_shells = set(Shell.objects.filter(user=request_user).values_list("shell_url", flat=True))

        # Filter out duplicate shell URLs
        new_shells = [Shell(**data) for data in shells_data if data["shell_url"] not in existing_shells]

        if not new_shells:
            return {"message": b"No new Shells were created. All provided Shells already exist.", b"created_count": 0}

        try:
            # Bulk create only new Shells
            created_shells = Shell.objects.bulk_create(new_shells)
            for instance in created_shells:
                post_save.send(sender=Shell, instance=instance, created=True)
            return {
                "message": f"{len(created_shells)} Shells created successfully.",
                "created_count": len(created_shells),
            }
        except IntegrityError:
            return {"message": "Some Shells were skipped due to duplication."}
