from abc import abstractmethod
from typing import Protocol


class IEncryptionHelper(Protocol):
    @abstractmethod
    def encrypt(self, plaintext: str) -> str: ...

    @abstractmethod
    def decrypt(self, encrypted_text: str) -> str: ...

    @abstractmethod
    def encrypt_for_user(self, plaintext: str, salt_b64: str) -> str: ...

    @abstractmethod
    def decrypt_for_user(self, encrypted_text: str, salt_b64: str) -> str: ...
