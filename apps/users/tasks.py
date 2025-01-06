import logging

from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import get_template

logger = logging.getLogger(__name__)


@shared_task
def send_email_notification(subject, template, from_email, to_email, user_name, code):
    """
    Send an HTML email notification to a user.

    Args:
        subject (str): Email subject line
        template (str): Path to the email template
        from_email (str): Sender's email address
        to_email (list): List of recipient email addresses
        user_name (str): Name of the recipient
        code (str): Verification or reset code to include in the email
    """
    try:
        # Render the HTML template with context
        email_template = get_template(template).render({"user_name": user_name, "code": code})

        # Create and configure the email message
        email = EmailMessage(subject=subject, body=email_template, from_email=from_email, to=to_email)
        email.content_subtype = "html"

        # Send the email
        email.send()
        logger.info(f"Email notification sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email notification to {to_email}: {str(e)}")
        raise e
