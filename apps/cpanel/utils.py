import logging
import socket

logger = logging.getLogger(__name__)


def check_cpanel_status(domain):
    """Check cPanel server status (ports, SSL, DNS, etc.)
    {
    'port_checks':
        {
            'cPanel HTTP': 'Open',
            'cPanel HTTPS': 'Open',
            'WHM HTTP': 'Open',
            'WHM HTTPS': 'Open',
            'FTP': 'Open',
            'SMTP': 'Closed',
            'DNS': 'Open'
        },
    }
    """
    logger.info(f"Checking cPanel status for domain: {domain}")
    results = {}
    cpanel_ports = {
        2082: "cPanel HTTP",
        2083: "cPanel HTTPS",
        2086: "WHM HTTP",
        2087: "WHM HTTPS",
        21: "FTP",
        25: "SMTP",
        53: "DNS",
    }
    results["port_checks"] = {}
    for port, service in cpanel_ports.items():
        logger.debug(f"Checking port {port} for service: {service}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((domain, port))
        status = "Open" if result == 0 else "Closed"
        results["port_checks"][service] = status
        logger.debug(f"Port {port} ({service}) status: {status}")
        sock.close()

    logger.info(f"Completed cPanel status check for {domain}")
    return results
