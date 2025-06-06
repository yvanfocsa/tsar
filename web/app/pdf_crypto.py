
import os
from cryptography.fernet import Fernet, InvalidToken
_key = os.environ.get("PDF_ENC_KEY")
if not _key:
    raise RuntimeError("PDF_ENC_KEY missing")
FERNET = Fernet(_key)
def encrypt(data: bytes) -> bytes:
    return FERNET.encrypt(data)
def decrypt(token: bytes) -> bytes:
    try:
        return FERNET.decrypt(token)
    except InvalidToken as e:
        raise ValueError("Invalid key / data") from e
