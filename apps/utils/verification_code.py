import random
import string


def generate_verification_code():
    """
    Generates a random 6-character verification code using uppercase letters and digits.
    Returns:
        str: A random string containing 6 characters (uppercase letters and numbers)
    """
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
