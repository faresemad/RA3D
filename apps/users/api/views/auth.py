import logging

from django.contrib.auth import get_user_model, login
from django.utils.crypto import get_random_string
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api.serializers.auth import (
    LoginSerializer,
    LogoutSerializer,
    ResendActivationCodeSerializer,
    SignUpSerializer,
)
from apps.users.api.serializers.profile import UserInformationSuccessLoginSerializer
from apps.users.api.serializers.validation import (
    AccountActivationSerializer,
    EmailChangeSerializer,
    EmailChangeVerifySerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetVerifySerializer,
)
from apps.users.models import ActivationCode
from apps.users.tasks import send_email_notification
from apps.utils.verification_code import generate_verification_code

logger = logging.getLogger(__name__)


class Login(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = LoginSerializer

    def get_tokens_for_user(self, user):
        """Generate JWT tokens for authenticated user"""
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    def handle_successful_login(self, request, user):
        """Handle successful login operations"""
        tokens = self.get_tokens_for_user(user)
        login(request, user)
        logger.info(f"User  {user.id} logged in successfully")

        # Create the response data
        response_data = {
            "user_id": user.id,
            **tokens,
            "success": "Login successful",
            "user": UserInformationSuccessLoginSerializer(user, context={"request": request}).data,
        }

        # Create the response object
        response = Response(response_data)

        return response

    def handle_login_error(self, user):
        """Handle various login error scenarios"""
        if user is not None and not user.email_confirmed:
            logger.warning(f"Login attempt for unconfirmed email: {user.email}")
            return Response(
                {"error": "Email not confirmed, please activate your account", "user_id": user.id, "email": user.email},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        logger.warning("Invalid login attempt")
        return Response({"error": "Invalid Email or password"}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        """Handle login request"""
        logger.info("Attempting user login")
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Login validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data.get("user")

        if user is not None and user.email_confirmed:
            return self.handle_successful_login(request, user)  # Return the Response object directly

        return self.handle_login_error(user)


class AccountActivation(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = AccountActivationSerializer

    def create(self, request, *args, **kwargs):
        logger.info("Attempting account activation")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activation_code = serializer.validated_data["code"]
        email = serializer.validated_data["email"]
        email_confirmed = ActivationCode.objects.filter(activation_code=activation_code, user__email=email).first()

        if not email_confirmed or not email_confirmed.verify_activation_code(activation_code):
            logger.warning(f"Invalid activation code for user {email}")
            return Response({"error": "Invalid activation code"}, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"Account activated for user {email}")
        return Response({"success": "Account Activated"}, status=status.HTTP_200_OK)


class ResendActivationCode(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = ResendActivationCodeSerializer

    def create(self, request, *args, **kwargs):
        """
        Resends activation code to user's email.
        """
        logger.info("Attempting to resend activation code")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = get_user_model().objects.get(email=email)
            if user.email_confirmed:
                logger.warning(f"Resend activation attempt for already confirmed account: {user.email}")
                return Response({"error": "Account already activated"}, status=status.HTTP_400_BAD_REQUEST)

            activation_code = ActivationCode.objects.get(user=user)
            activation_code.create_activation_code()

            subject = "Your New Activation Code - [RA3D]"
            from_email = "<my email>"
            to_email = [user.email]
            send_email_notification.delay(
                subject, "activation.html", from_email, to_email, user.username, activation_code.activation_code
            )

            logger.info(f"New activation code sent to user {user.id}")
            return Response({"success": "New activation code sent to your email"}, status=status.HTTP_200_OK)

        except get_user_model().DoesNotExist:
            logger.warning(f"Resend activation attempt for non-existent user: {email}")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except ActivationCode.DoesNotExist:
            logger.warning(f"No activation code found for user: {email}")
            return Response({"error": "No activation code found"}, status=status.HTTP_404_NOT_FOUND)


class SignUp(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SignUpSerializer

    def perform_create(self, serializer):
        """
        Creates a new user and an activation code associated with the user.
        """
        user = serializer.save()
        activation_code = ActivationCode(user=user)
        activation_code.create_activation_code()
        self.send_activation_email(user, activation_code)
        logger.info(f"User {user.id} signed up successfully")
        return user

    def send_activation_email(self, user, activation_code):
        """
        Sends an activation email to the user with the activation code.
        """
        subject = "Your Activation Code - [RA3D]"
        from_email = "<my email>"
        to_email = [user.email]
        send_email_notification.delay(
            subject, "activation.html", from_email, to_email, user.username, activation_code.activation_code
        )

    def create(self, request, *args, **kwargs):
        """
        Handles the sign up request.
        """
        logger.info("Attempting user sign up")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        if get_user_model().objects.filter(email=email).exists():
            logger.warning(f"Sign up attempt with existing email: {email}")
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = self.perform_create(serializer)
        return Response(
            {
                "success": "Account created, check your email for activation code",
                "user_id": user.id,
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class Logout(viewsets.ViewSet):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Handles user logout by invalidating their current session.
        Requires user to be authenticated to access this endpoint.
        Returns a success message upon successful logout.
        """
        logger.info(f"User {request.user.id} logged out")
        request.session.flush()
        response = Response({"success": "Logout successful"}, status=status.HTTP_200_OK)
        return response


class PasswordReset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for handling password reset functionality.
    Allows users to request a password reset by providing their email.
    """

    serializer_class = PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        """
        Handles password reset request.
        Generates and sends a verification code to user's email.

        Args:
            request: HTTP request object containing user's email

        Returns:
            Response with success message if email is valid,
            or error message if email doesn't exist
        """
        logger.info("Attempting password reset")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            logger.warning(f"Password reset attempt for non-existent email: {email}")
            return Response({"error": "Email not found"}, status=status.HTTP_400_BAD_REQUEST)

        self._handle_verification_code(user)
        self._send_reset_email(user)

        return Response({"success": "Password reset code sent to email"}, status=status.HTTP_200_OK)

    def _handle_verification_code(self, user):
        """Helper method to generate and save verification code"""
        code = generate_verification_code()
        user.email_verification_code = code
        user.save(update_fields=["email_verification_code"])
        return code

    def _send_reset_email(self, user):
        """Helper method to send reset email"""
        subject = "Password Reset Code - RA3D"
        from_email = "<my email>"
        to_email = [user.email]

        send_email_notification.delay(
            subject=subject,
            template="reset-password.html",
            from_email=from_email,
            to_email=to_email,
            user_name=user.username,
            code=user.email_verification_code,
        )


class PasswordResetVerify(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = PasswordResetVerifySerializer

    def create(self, request, *args, **kwargs):
        """
        Verifies password reset code and sets new password.

        Args:
            request: HTTP request containing new password and verification code

        Returns:
            Response with success message if code is valid,
            or error message if code doesn't exist
        """
        logger.info("Attempting password reset verification")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]
        code = serializer.validated_data["code"]

        try:
            user = self._get_user_by_code(code)
            self._reset_password(user, new_password)
            logger.info(f"Password reset successful for user {user.id}")
            return Response({"success": "Password reset successful"}, status=status.HTTP_200_OK)
        except get_user_model().DoesNotExist:
            logger.warning(f"Invalid password reset code: {code}")
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

    def _get_user_by_code(self, code):
        """Helper method to get user by verification code"""
        return get_user_model().objects.get(email_verification_code=code)

    def _reset_password(self, user, new_password):
        """Helper method to reset user password"""
        user.set_password(new_password)
        user.email_verification_code = None
        user.save(update_fields=["password", "email_verification_code"])


class PasswordChange(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def create(self, request, *args, **kwargs):
        """
        Changes user password after validating old password.

        Args:
            request: HTTP request containing old and new passwords

        Returns:
            Response with success message if password change is successful,
            or error message if old password is invalid
        """
        logger.info(f"Attempting password change for user {request.user.id}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_password = serializer.validated_data["new_password"]
        old_password = serializer.validated_data["old_password"]

        if not self._validate_old_password(user, old_password):
            return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

        self._change_password(user, new_password)
        return Response({"success": "Password changed successfully"}, status=status.HTTP_200_OK)

    def _validate_old_password(self, user, old_password):
        """Helper method to validate old password"""
        if not user.check_password(old_password):
            logger.warning(f"Invalid old password for user {user.id}")
            return False
        return True

    def _change_password(self, user, new_password):
        """Helper method to change user password"""
        user.set_password(new_password)
        user.save(update_fields=["password"])
        logger.info(f"Password changed successfully for user {user.id}")


class EmailChange(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailChangeSerializer

    def create(self, request, *args, **kwargs):
        """
        Handles email change request by sending verification code.

        Args:
            request: HTTP request containing new email

        Returns:
            Response with success message if verification code is sent,
            or error message if email is invalid
        """
        logger.info(f"Attempting email change for user {request.user.id}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_email = serializer.validated_data["email"]

        if not self._validate_new_email(user, new_email):
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)

        self._send_verification_code(user, new_email)
        return Response({"success": "Email change code sent to email"}, status=status.HTTP_200_OK)

    def _validate_new_email(self, user, new_email):
        """Helper method to validate new email"""
        if get_user_model().objects.filter(email=new_email).exists():
            logger.warning(f"Email change attempt with existing email: {new_email}")
            return False
        if user.email == new_email:
            logger.warning(f"Email change attempt with same email: {new_email}")
            return False
        return True

    def _send_verification_code(self, user, new_email):
        """Helper method to send verification code"""
        code = get_random_string(length=6)
        user.email_verification_code = code
        user.new_email = new_email
        user.save(update_fields=["email_verification_code", "new_email"])

        subject = "Email Change Verification - RA3D"
        from_email = "<my email>"
        to_email = [new_email]

        send_email_notification.delay(
            subject=subject,
            template="change-email.html",
            from_email=from_email,
            to_email=to_email,
            user_name=user.username,
            code=code,
        )


class EmailChangeVerify(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmailChangeVerifySerializer

    def create(self, request, *args, **kwargs):
        """
        Verifies email change code and updates user's email if valid.

        Args:
            request: HTTP request containing verification code and new email

        Returns:
            Response with success message if email is changed,
            or error message if verification fails
        """
        logger.info(f"Attempting email change verification for user {request.user.id}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        code = serializer.validated_data["code"]
        new_email = serializer.validated_data["new_email"]

        if not self._validate_verification_code(user, code):
            return Response({"error": "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        if user.new_email != new_email:
            logger.warning(f"Email verification attempt with mismatched email for user {user.id}")
            return Response({"error": "Email does not match the one sent"}, status=status.HTTP_400_BAD_REQUEST)

        if self._is_email_taken(new_email, user):
            logger.warning(f"Email {new_email} is already taken")
            return Response({"error": "Email is already taken"}, status=status.HTTP_400_BAD_REQUEST)

        self._update_user_email(user, new_email)
        return Response({"success": "Email changed successfully"}, status=status.HTTP_200_OK)

    def _validate_verification_code(self, user, code):
        """Helper method to validate verification code"""
        if user.email_verification_code != code:
            logger.warning(f"Invalid email change code for user {user.id}")
            return False
        return True

    def _update_user_email(self, user, new_email):
        """Helper method to update user's email"""
        user.email = new_email
        user.email_verification_code = None
        user.save(update_fields=["email", "email_verification_code"])
        logger.info(f"Email changed successfully for user {user.id}")

    def _is_email_taken(self, email, current_user):
        """Helper method to check if email is already taken by another user"""
        return get_user_model().objects.exclude(id=current_user.id).filter(email=email).exists()
