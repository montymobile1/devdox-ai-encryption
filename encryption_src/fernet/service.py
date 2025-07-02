import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from encryption_src.base import constants
from encryption_src.base.exceptions import MissingEncryptionKeyError
from encryption_src.base.interface import IEncryptionHelper


class FernetEncryptionHelper(IEncryptionHelper):

    def __init__(self, secret_key: str):
        if not secret_key:
            raise MissingEncryptionKeyError(constants.ENCRYPTION_KEY_NOT_FOUND)

        self.secret_key = secret_key

    def encrypt(self, plaintext: str) -> str:
        return Fernet(self.secret_key).encrypt(plaintext.encode()).decode()

    def decrypt(self, encrypted_text: str) -> str:
        return Fernet(self.secret_key).decrypt(encrypted_text.encode()).decode()

    def encrypt_for_user(self, plaintext: str, salt_b64: str) -> str:
        salt_bytes = base64.urlsafe_b64decode(salt_b64.encode())
        cipher = Fernet(self._derive_key(salt_bytes))
        return cipher.encrypt(plaintext.encode()).decode()

    def decrypt_for_user(self, encrypted_text: str, salt_b64: str) -> str:
        salt_bytes = base64.urlsafe_b64decode(salt_b64.encode())
        cipher = Fernet(self._derive_key(salt_bytes))
        return cipher.decrypt(encrypted_text.encode()).decode()

    def _derive_key(self, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000
        )
        return base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
