from decimal import Decimal

import pandas as pd
from django.db.models.signals import post_save
from rest_framework import serializers

from apps.rdp.models import Rdp, RdpStatus, RdpType, RdpUserAccessType, RdpWindowsType
from apps.users.api.serializers.profile import UserProfileSerializer


class RdpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rdp
        fields = [
            "id",
            "ip",
            "hosting",
            "location",
            "username",
            "password",
            "ram_size",
            "cpu_cores",
            "price",
            "rdp_type",
            "status",
            "windows_type",
            "access_type",
            "details",
            "created_at",
            "is_deleted",
        ]


class RdpListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    ip = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = Rdp
        fields = [
            "id",
            "hosting",
            "location",
            "user",
            "ip",
            "username",
            "ram_size",
            "cpu_cores",
            "price",
            "rdp_type",
            "status",
            "windows_type",
            "access_type",
            "created_at",
        ]

    def get_ip(self, obj: Rdp):
        ip_parts = obj.ip.split(".")
        return f"{ip_parts[0]}.{ip_parts[1]}.*.*"

    def get_username(self, obj: Rdp):
        return f"{obj.username[:2]}***"


class CreateRdpSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rdp
        fields = [
            "user",
            "ip",
            "username",
            "password",
            "ram_size",
            "cpu_cores",
            "price",
            "rdp_type",
            "windows_type",
            "access_type",
        ]


class BulkUploadRdpSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate(self, attrs):
        """Validate and parse the uploaded file."""
        file = attrs.get("file", None)
        if not file:
            raise serializers.ValidationError("No file uploaded.")

        file_extension = file.name.split(".")[-1].lower()

        if file_extension not in ["xlsx", "txt"]:
            raise serializers.ValidationError("Only .xlsx (Excel) and .txt files are supported.")

        rdps = []
        errors = []

        # Read XLSX File
        if file_extension == "xlsx":
            try:
                df = pd.read_excel(file)
            except Exception as e:
                raise serializers.ValidationError(f"Error reading Excel file: {str(e)}")

            expected_columns = [
                "ip",
                "username",
                "password",
                "ram_size",
                "cpu_cores",
                "price",
                "rdp_type",
                "windows_type",
                "access_type",
            ]

            # Check if all required columns exist
            if not all(col in df.columns for col in expected_columns):
                raise serializers.ValidationError(f"Excel file must contain columns: {', '.join(expected_columns)}")

            # Parse each row
            for index, row in df.iterrows():
                try:
                    ip = str(row["ip"]).strip()
                    username = str(row["username"]).strip()
                    password = str(row["password"]).strip()
                    ram_size = int(row["ram_size"])
                    cpu_cores = int(row["cpu_cores"])
                    price = Decimal(row["price"])
                    rdp_type = str(row["rdp_type"]).strip()
                    windows_type = str(row["windows_type"]).strip()
                    access_type = str(row["access_type"]).strip()

                    # Validation
                    if price < 1:
                        errors.append(f"Row {index + 2}: Price must be at least 1")
                    if rdp_type not in dict(RdpType.choices):
                        errors.append(f"Row {index + 2}: Invalid RDP type '{rdp_type}'")
                    if windows_type not in dict(RdpWindowsType.choices):
                        errors.append(f"Row {index + 2}: Invalid Windows type '{windows_type}'")
                    if access_type not in dict(RdpUserAccessType.choices):
                        errors.append(f"Row {index + 2}: Invalid access type '{access_type}'")

                    if not errors:
                        rdps.append(
                            {
                                "ip": ip,
                                "username": username,
                                "password": password,
                                "ram_size": ram_size,
                                "cpu_cores": cpu_cores,
                                "price": price,
                                "rdp_type": rdp_type,
                                "status": RdpStatus.UNSOLD,  # Default status to UNSOLD
                                "windows_type": windows_type,
                                "access_type": access_type,
                                "location": None,  # Default to None
                                "hosting": None,  # Default to None
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
                if len(parts) != 9:  # ✅ Expecting exactly 9 columns now
                    errors.append(f"Line {index}: Incorrect number of columns (Expected 9, got {len(parts)})")
                    continue

                ip, username, password, ram_size, cpu_cores, price, rdp_type, windows_type, access_type = (
                    p.strip() for p in parts
                )

                try:
                    ram_size = int(ram_size)
                    cpu_cores = int(cpu_cores)
                    price = Decimal(price)
                    if price < 1:
                        errors.append(f"Line {index}: Price must be at least 1")
                except Exception:
                    errors.append(f"Line {index}: Invalid numeric format for ram_size, cpu_cores, or price")

                if rdp_type not in dict(RdpType.choices):
                    errors.append(f"Line {index}: Invalid RDP type '{rdp_type}'")
                if windows_type not in dict(RdpWindowsType.choices):
                    errors.append(f"Line {index}: Invalid Windows type '{windows_type}'")
                if access_type not in dict(RdpUserAccessType.choices):
                    errors.append(f"Line {index}: Invalid access type '{access_type}'")

                if not errors:
                    rdps.append(
                        {
                            "ip": ip,
                            "username": username,
                            "password": password,
                            "ram_size": ram_size,
                            "cpu_cores": cpu_cores,
                            "price": price,
                            "rdp_type": rdp_type,
                            "status": RdpStatus.UNSOLD,  # Default status to UNSOLD
                            "windows_type": windows_type,
                            "access_type": access_type,
                            "location": None,  # Default to None
                            "hosting": None,  # Default to None
                            "details": {},
                        }
                    )

        if errors:
            raise serializers.ValidationError({"errors": errors})

        attrs["rdps"] = rdps  # ✅ Ensure 'rdps' key exists
        return attrs

    def create(self, validated_data):
        """Bulk create RDP records"""
        request_user = self.context["request"].user  # Get the user from the request
        rdps_data = validated_data["rdps"]

        # Assign user to all RDP records
        for rdp_data in rdps_data:
            rdp_data["user"] = request_user

        # Bulk create RDP instances
        rdp_instances = Rdp.objects.bulk_create([Rdp(**data) for data in rdps_data])

        for instance in rdp_instances:
            post_save.send(sender=Rdp, instance=instance, created=True)

        return rdp_instances
