# payments/signature.py
import uuid
import hmac
import hashlib
import base64
from typing import Mapping, Sequence


def build_signed_string_from_fields(field_names: Sequence[str], data: Mapping[str, str], sep: str = ",") -> str:
    """
    Build the eSewa signing string in the format:
        name1=value1,name2=value2,...
    using the order of field_names.
    Missing fields are treated as empty strings.
    """
    parts = []
    for name in field_names:
        value = str(data.get(name, ""))  # Safe: defaults to empty string
        parts.append(f"{name}={value}")
    signed_string = sep.join(parts)
    return signed_string


def generate_esewa_signature(secret_key: str, message: str) -> str:
    """
    Generate HMAC-SHA256 signature and return Base64-encoded string.
    """
    if not secret_key or not message:
        raise ValueError("Secret key and message must be provided for signature generation")

    key_bytes = secret_key.encode("utf-8")
    message_bytes = message.encode("utf-8")

    hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha256)
    digest = hmac_obj.digest()

    signature = base64.b64encode(digest).decode("utf-8")
    return signature


def generate_transaction_uuid() -> str:
    """
    Generate a unique transaction UUID for eSewa payment.
    Format: standard UUID string.
    """
    return str(uuid.uuid4())
