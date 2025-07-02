"""
FakeEncryptionHelper is a test double for IEncryptionHelper.

This fake is designed to:
- Simulate predictable encryption/decryption behavior without real crypto
- Record calls and arguments for interaction testing (spy behavior)
- Be injected in place of FernetEncryptionHelper via dependency injection (e.g., FastAPI Depends)

Usage Examples (doctest style):

Basic encrypt/decrypt round-trip:
    >>> fake = FakeEncryptionHelper()
    >>> token = fake.encrypt("hello")
    >>> fake.decrypt(token)
    'hello'

User-specific encryption round-trip:
    >>> token = fake.encrypt_for_user("world", "abc123")
    >>> fake.decrypt_for_user(token, "abc123")
    'world'

Unknown token returns placeholder:
    >>> fake.decrypt("not-issued")
    '<unknown>'
    >>> fake.decrypt_for_user("invalid-token", "abc123")
    '<unknown>'

Verify method interactions:
    >>> fake.called_with("encrypt", "hello")
    True
    >>> fake.called_with("decrypt", "enc-0")
    True

Reset call history:
    >>> fake.clear_calls()
    >>> fake.received_calls
    []

Note:
- This fake returns '<unknown>' for tokens it didn't issue.
- The token format is internal and should not be relied upon in application logic.

"""

from typing import Any

from encryption_src.base.interface import IEncryptionHelper


class FakeEncryptionHelper(IEncryptionHelper):
    def __init__(self):
        self.encrypted_store = {}
        self.received_calls = []
        self._counter = 0

    def encrypt(self, plaintext: str) -> str:
        self.received_calls.append(("encrypt", plaintext))
        token = f"enc-{self._counter}"
        self._counter += 1
        self.encrypted_store[token] = plaintext
        return token

    def decrypt(self, encrypted_text: str) -> str:
        self.received_calls.append(("decrypt", encrypted_text))
        return self.encrypted_store.get(encrypted_text, "<unknown>")

    def encrypt_for_user(self, plaintext: str, salt_b64: str) -> str:
        self.received_calls.append(("encrypt_for_user", plaintext, salt_b64))
        token = f"userenc-{salt_b64}-{self._counter}"
        self._counter += 1
        self.encrypted_store[token] = plaintext
        return token

    def decrypt_for_user(self, encrypted_text: str, salt_b64: str) -> str:
        self.received_calls.append(("decrypt_for_user", encrypted_text, salt_b64))
        return self.encrypted_store.get(encrypted_text, "<unknown>")

    def called_with(self, method: str, *args: Any) -> bool:
        return any(
            call[0] == method and call[1:] == args for call in self.received_calls
        )

    def clear_calls(self):
        self.received_calls.clear()
