import logging

import requests
from celery import shared_task

from apps.smtp.models import SMTP

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def get_domain_info(self, id):
    """Get SEO, hosting, and ip metrics for ips you legally own."""
    smtp = SMTP.objects.get(id=id)
    ip = smtp.ip
    logger.info(f"Starting ip info collection for {ip}")
    result = {}

    try:
        ip_info = requests.get(f"https://ipinfo.io/{ip}/json").json()
        result.update(
            {
                "IP": ip,
                "Hosting": ip_info.get("org", "Unknown"),
                "Location": f"{ip_info.get('city')}, {ip_info.get('country')}",
            }
        )
        logger.debug(f"Successfully retrieved IP and hosting info for {ip}")
    except Exception as e:
        logger.error(f"Failed to get IP/Hosting info for {ip}: {str(e)}")
        result["Error"] = f"IP/Hosting Error: {str(e)}"

    logger.info(f"Completed ip info collection for {ip}")

    smtp.hosting = result.get("Hosting")
    smtp.location = result.get("Location")
    smtp.save()
    return result
