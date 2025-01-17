import logging
import socket

import requests
from celery import shared_task

from apps.shells.models import Shell

logger = logging.getLogger(__name__)


@shared_task
def fetch_shell_details(shell_id):
    """Fetch the IP address and machine details for the given Shell object."""
    try:
        shell = Shell.objects.get(id=shell_id)

        # Extract hostname from URL
        url = shell.shell_url
        if url.startswith("http://") or url.startswith("https://"):
            url = url.split("://")[1].split("/")[0]

        logger.info(f"Extracted hostname: {url}")
        # Fetch IP information from ipinfo.io
        ip_address = socket.gethostbyname(url)
        ip_info_response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        ip_info = ip_info_response.json()

        # Remove unwanted fields from IP info
        ip_info.pop("ip", None)
        ip_info.pop("readme", None)
        ip_info.pop("hostname", None)

        # Fetch HTTP headers to infer machine type
        headers_response = requests.head(f"http://{url}", timeout=10)
        headers = headers_response.headers

        # Infer OS from Server header
        server_header = headers.get("Server", "").lower()
        if "nginx" in server_header or "apache" in server_header:
            os_type = "Linux/Unix-like"
            logger.info(f"Detected Linux/Unix-like server: {server_header}")
        elif "microsoft-iis" in server_header:
            os_type = "Windows"
            logger.info(f"Detected Windows server: {server_header}")
        else:
            os_type = "Unknown"
            logger.info(f"Could not infer OS from server header: {server_header}")

        # Update the details field of the shell
        shell.details = {
            "IP Info": ip_info,
            "Server Header": server_header,
            "Inferred OS": os_type,
        }
        shell.save()
        logger.info(f"Successfully updated details for Shell {shell_id}")

    except Exception as e:
        logger.exception(f"Error fetching details for Shell {shell_id}: {e}")
