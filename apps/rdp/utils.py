import logging
import socket

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
