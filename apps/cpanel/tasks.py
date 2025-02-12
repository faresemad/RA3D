import logging
import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse

import requests
import whois
from celery import shared_task

from apps.cpanel.models import CPanel

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def get_domain_info(self, id):
    """Get SEO, hosting, and domain metrics for domains you legally own."""
    cpanel = CPanel.objects.get(id=id)
    domain = cpanel.host
    logger.info(f"Starting domain info collection for {domain}")
    result = {}

    # Get IP and Hosting Info
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

    # SSL Check
    try:
        cert = ssl.get_server_certificate((domain, 443))
        x509 = ssl.PEM_cert_to_DER_cert(cert)
        result["SSL"] = "Valid" if x509 else "Invalid"
        logger.debug(f"SSL check completed for {domain}")
    except Exception as e:
        logger.warning(f"SSL check failed for {domain}: {str(e)}")
        result["SSL"] = "No SSL"

    # TLD Extraction
    try:
        parsed_url = urlparse(domain)
        if parsed_url.scheme and parsed_url.netloc:
            result["TLD"] = parsed_url.netloc.split(".")[-1]
        else:
            result["TLD"] = domain.split(".")[-1] if "." in domain else None
    except Exception:
        result["TLD"] = None
    logger.debug(f"TLD extracted for {domain}")

    # Domain Age
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        result["Domain Age"] = f"{(datetime.now() - creation_date).days} days"
    except Exception as e:
        logger.error(f"Failed to get domain age for {domain}: {str(e)}")
        result["Domain Age"] = "Unknown"

    logger.info(f"Completed domain info collection for {domain}")

    cpanel.ssl = True if result.get("SSL") == "Valid" else False
    cpanel.tld = result.get("TLD")
    cpanel.hosting = result.get("Hosting")
    cpanel.location = result.get("Location")
    cpanel.details = result
    cpanel.save()
    return result
