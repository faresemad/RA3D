import logging
from decimal import Decimal

import pandas as pd
from django.db.models.signals import post_save
from rest_framework import serializers

from apps.smtp.models import SMTP, SmtpStatus, SMTPType
from apps.users.api.serializers.profile import UserProfileSerializer

logger = logging.getLogger(__name__)


class SmtpListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    ip = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = SMTP
        fields = [
            "id",
            "user",
            "ip",
            "username",
            "hosting",
            "location",
            "port",
            "smtp_type",
            "status",
            "price",
            "created_at",
        ]

    def get_ip(self, obj: SMTP):
        ip_parts = obj.ip.split(".")
        return f"{ip_parts[0]}.{ip_parts[1]}.*.*"

    def get_username(self, obj: SMTP):
        return f"{obj.username[:2]}***"


class SmtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTP
        fields = [
            "id",
            "ip",
            "port",
            "username",
            "password",
            "hosting",
            "location",
            "smtp_type",
            "status",
            "price",
            "created_at",
            "is_deleted",
        ]


class CreateSmtpSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = SMTP
        fields = [
            "id",
            "user",
            "ip",
            "port",
            "username",
            "password",
            "smtp_type",
            "price",
        ]


class BulkCreateSMTPTextSerializer(serializers.Serializer):
    data = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Parse textarea input and validate each SMTP entry.
        Expected format:
        ip | port | username | password | smtp_type | price
        """
        logger.info("Starting validation of bulk SMTP data")
        value = attrs.get("data", "").strip()
        lines = value.split("\n")
        smtps = []
        errors = []

        logger.debug(f"Processing {len(lines)} lines of SMTP data")
        for index, line in enumerate(lines, start=1):
            parts = line.split("|")
            if len(parts) != 6:
                logger.warning(f"Line {index} has incorrect number of columns: {len(parts)}")
                errors.append(f"Line {index}: Incorrect number of columns (Expected 6, got {len(parts)})")
                continue

            ip, port, username, password, smtp_type, price = (p.strip() for p in parts)

            try:
                port = int(port)
                price = Decimal(price)
                if price < 1:
                    errors.append(f"Line {index}: Price must be at least 1")
            except ValueError:
                errors.append(f"Line {index}: Invalid format for port or price")

            if smtp_type not in dict(SMTPType.choices):
                errors.append(f"Line {index}: Invalid SMTP type '{smtp_type}'")

            if not errors:
                smtps.append(
                    {
                        "ip": ip,
                        "port": port,
                        "username": username,
                        "password": password,
                        "smtp_type": smtp_type,
                        "price": price,
                        "status": SmtpStatus.UNSOLD,  # Default status to UNSOLD
                    }
                )

        if errors:
            raise serializers.ValidationError({"errors": errors})

        logger.info(f"Validation completed successfully. {len(smtps)} SMTPs ready for creation")
        return {"smtps": smtps}

    def create(self, validated_data):
        """Bulk create SMTP records, skipping duplicates"""
        request_user = self.context["request"].user
        smtps_data = validated_data["smtps"]

        # Fetch existing SMTPs for this user based on (ip, port)
        existing_smtps = set(SMTP.objects.filter(user=request_user).values_list("ip", "port"))

        # Filter out duplicate SMTPs
        new_smtps = [
            SMTP(**data, user=request_user) for data in smtps_data if (data["ip"], data["port"]) not in existing_smtps
        ]

        if not new_smtps:
            return {"message": "No new SMTPs were created. All provided SMTPs already exist.", "created_count": 0}

        created_smtps = SMTP.objects.bulk_create(new_smtps)
        logger.info(f"Created {len(created_smtps)} SMTPs")

        # Manually trigger the post_save signal
        for instance in created_smtps:
            post_save.send(sender=SMTP, instance=instance, created=True)

        return {"message": f"{len(created_smtps)} SMTPs created successfully.", "created_count": len(created_smtps)}


class BulkUploadSMTPSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate(self, attrs):
        """Validate and parse the uploaded file."""
        file = attrs.get("file", None)
        if not file:
            raise serializers.ValidationError("No file uploaded.")

        file_extension = file.name.split(".")[-1].lower()

        if file_extension not in ["xlsx", "txt"]:
            raise serializers.ValidationError("Only .xlsx (Excel) and .txt files are supported.")

        smtps = []
        errors = []

        # Read XLSX File
        if file_extension == "xlsx":
            try:
                df = pd.read_excel(file)
            except Exception as e:
                raise serializers.ValidationError(f"Error reading Excel file: {str(e)}")

            expected_columns = ["ip", "port", "username", "password", "smtp_type", "price"]

            # Check if all required columns exist
            if not all(col in df.columns for col in expected_columns):
                raise serializers.ValidationError(f"Excel file must contain columns: {', '.join(expected_columns)}")

            # Parse each row
            for index, row in df.iterrows():
                try:
                    ip = str(row["ip"]).strip()
                    port = int(row["port"])
                    username = str(row["username"]).strip()
                    password = str(row["password"]).strip()
                    smtp_type = str(row["smtp_type"]).strip()
                    price = Decimal(row["price"])

                    if price < 1:
                        errors.append(f"Row {index + 2}: Price must be at least 1")
                    if smtp_type not in dict(SMTPType.choices):
                        errors.append(f"Row {index + 2}: Invalid SMTP type '{smtp_type}'")

                    if not errors:
                        smtps.append(
                            {
                                "ip": ip,
                                "port": port,
                                "username": username,
                                "password": password,
                                "smtp_type": smtp_type,
                                "price": price,
                                "status": SmtpStatus.UNSOLD,
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
                if len(parts) != 6:
                    errors.append(f"Line {index}: Incorrect number of columns (Expected 6, got {len(parts)})")
                    continue

                ip, port, username, password, smtp_type, price = (p.strip() for p in parts)

                try:
                    port = int(port)
                    price = Decimal(price)
                    if price < 1:
                        errors.append(f"Line {index}: Price must be at least 1")
                except ValueError:
                    errors.append(f"Line {index}: Invalid format for port or price")

                if smtp_type not in dict(SMTPType.choices):
                    errors.append(f"Line {index}: Invalid SMTP type '{smtp_type}'")

                if not errors:
                    smtps.append(
                        {
                            "ip": ip,
                            "port": port,
                            "username": username,
                            "password": password,
                            "smtp_type": smtp_type,
                            "price": price,
                            "status": SmtpStatus.UNSOLD,
                        }
                    )

        if errors:
            raise serializers.ValidationError({"errors": errors})

        attrs["smtps"] = smtps
        return attrs

    def create(self, validated_data):
        """Bulk create SMTP records, skipping duplicates"""
        request_user = self.context["request"].user
        smtps_data = validated_data["smtps"]

        # Fetch existing SMTPs for this user
        existing_smtps = set(SMTP.objects.filter(user=request_user).values_list("ip", "port"))

        # Filter out duplicate SMTPs
        new_smtps = [
            SMTP(**data, user=request_user) for data in smtps_data if (data["ip"], data["port"]) not in existing_smtps
        ]

        if not new_smtps:
            return {"message": "No new SMTPs were created. All provided SMTPs already exist.", "created_count": 0}

        created_smtps = SMTP.objects.bulk_create(new_smtps)
        logger.info(f"Created {len(created_smtps)} SMTPs")

        # Manually trigger the post_save signal
        for instance in created_smtps:
            post_save.send(sender=SMTP, instance=instance, created=True)

        return {"message": f"{len(created_smtps)} SMTPs created successfully.", "created_count": len(created_smtps)}
