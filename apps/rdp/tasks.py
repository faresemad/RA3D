import logging
import socket

import requests
from celery import shared_task

from apps.rdp.models import Rdp

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def get_ip_geolocation_and_hosting_info(target_id):
    """Fetch geolocation, hosting provider, and network info for a domain/IP."""
    rdp = Rdp.objects.get(id=target_id)
    target = rdp.ip
    logger.info(f"Fetching geolocation and hosting info for target: {target}")
    try:
        # Resolve domain to IP if input is a URL
        if not target.replace(".", "").isdigit():
            logger.debug(f"Resolving domain {target} to IP")
            target = socket.gethostbyname(target)
            logger.info(f"Resolved {target} to IP")

        # Fetch data from ipapi.co
        logger.debug("Fetching data from ipapi.co")
        ipapi_response = requests.get(f"https://ipapi.co/{target}/json/").json()
        logger.debug(f"Received response from ipapi.co: {ipapi_response}")

        # Extract location and ISP/hosting details
        location = (
            f"{ipapi_response.get('country_code')} - {ipapi_response.get('region')} - {ipapi_response.get('city')}"
        )
        hosting = ipapi_response.get("org", "Unknown")

        # Fetch data from IPinfo.io
        logger.debug("Fetching data from ipinfo.io")
        ipinfo_response = requests.get(f"https://ipinfo.io/{target}/json").json()
        logger.debug(f"Received response from ipinfo.io: {ipinfo_response}")

        asn = ipinfo_response.get("org", "Unknown")

        result = {
            "IP": target,
            "Location": location,
            "Hosting Provider": hosting,
            "ASN": asn,
            "ISP": ipapi_response.get("asn", {}),
            "Network": ipinfo_response.get("network", "Unknown"),
        }
        rdp.location = location
        rdp.hosting = hosting
        rdp.details = result
        rdp.save()
        logger.info(f"Successfully gathered information for {target}")
        return result

    except (socket.gaierror, requests.RequestException) as e:
        logger.error(f"Error gathering information for {target}: {str(e)}")
        return {"error": str(e)}
