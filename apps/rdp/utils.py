import logging
import socket

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def check_rdp_port(ip, port=3389, timeout=3):
    """Check if an RDP port is open (no credential extraction)."""
    logger.info(f"Checking RDP port {port} on IP {ip} with timeout {timeout}s")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            status = "Open" if result == 0 else "Closed"
            logger.info(f"Port {port} on {ip} is {status}")
            return status
    except OSError as e:
        logger.error(f"Error checking RDP port on {ip}: {str(e)}")
        return "Error"


def check_ip_blacklist(ip):
    """Check if IP is listed in common security blacklists."""
    logger.info(f"Checking IP {ip} against security blacklists")
    blacklist_results = {}

    if hasattr(settings, "ABUSEIPDB_API_KEY"):
        logger.info(f"Checking {ip} against AbuseIPDB")
        abuseipdb_response = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": settings.ABUSEIPDB_API_KEY},
            params={"ipAddress": ip, "maxAgeInDays": 90},
        )
        if abuseipdb_response.status_code == 200:
            data = abuseipdb_response.json().get("data", {})
            score = data.get("abuseConfidenceScore", 0)
            reports = data.get("totalReports")
            logger.info(f"AbuseIPDB results for {ip}: score={score}, reports={reports}")
            blacklist_results["abuseipdb"] = {
                "is_blacklisted": score > 25,
                "score": score,
                "reports": reports,
            }

    try:
        logger.info(f"Checking {ip} against Spamhaus")
        reversed_ip = ".".join(reversed(ip.split(".")))
        spamhaus_query = f"{reversed_ip}.zen.spamhaus.org"
        spamhaus_result = socket.gethostbyname_ex(spamhaus_query)[2]
        logger.info(f"Spamhaus lists for {ip}: {spamhaus_result}")
        blacklist_results["spamhaus"] = {"is_blacklisted": True, "lists": spamhaus_result}
    except socket.gaierror:
        logger.info(f"IP {ip} not found in Spamhaus blacklist")
        blacklist_results["spamhaus"] = {"is_blacklisted": False}

    return blacklist_results
