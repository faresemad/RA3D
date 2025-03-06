import logging
import socket

import requests
from celery import shared_task

from apps.webmails.models import WebMail

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def get_domain_info(self, id):
    """Get SEO, hosting, and domain metrics for domains you legally own."""
    webmail = WebMail.objects.get(id=id)
    domain = webmail.domain
    logger.info(f"Starting domain info collection for {domain}")
    result = {}

    try:
        ip = socket.gethostbyname(domain)
        ip_info = requests.get(f"https://ipinfo.io/{ip}/json").json()
        result.update(
            {
                "IP": ip,
                "Hosting": ip_info.get("org", "Unknown"),
                "Location": f"{ip_info.get('city')}, {ip_info.get('country')}",
            }
        )
        logger.debug(f"Successfully retrieved IP and hosting info for {domain}")
    except Exception as e:
        logger.error(f"Failed to get IP/Hosting info for {domain}: {str(e)}")
        result["Error"] = f"IP/Hosting Error: {str(e)}"

    logger.info(f"Completed domain info collection for {domain}")

    webmail.hosting = result.get("Hosting")
    webmail.location = result.get("Location")
    webmail.save()
    return result
