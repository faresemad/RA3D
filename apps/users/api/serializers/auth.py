from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"), email=email, password=password)

            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")

        else:
            msg = "Must include 'email' and 'password'."
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password], style={"input_type": "password"}
    )
    picture = serializers.ImageField(required=False)

    class Meta:
        model = get_user_model()
        fields = ["email", "username", "first_name", "last_name", "picture", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class LogoutSerializer(serializers.Serializer):
    pass  # No fields needed since it's just for logout


class ResendActivationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
