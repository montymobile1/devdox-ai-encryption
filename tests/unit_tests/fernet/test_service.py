import base64
import os

import pytest
from cryptography.fernet import Fernet, InvalidToken

from encryption_src.base import constants
from encryption_src.base.exceptions import MissingEncryptionKeyError
from encryption_src.base.interface import IEncryptionHelper
from encryption_src.fernet.service import FernetEncryptionHelper


class TestFernetEncryptionHelper:

    @pytest.fixture
    def helper(self):
        test_key = Fernet.generate_key().decode()
        return FernetEncryptionHelper(secret_key=test_key)

    def test_encrypt_decrypt_round_trip(self, helper):
        plaintext = "super-secret"
        encrypted = helper.encrypt(plaintext)
        decrypted = helper.decrypt(encrypted)
        assert decrypted == plaintext
        assert plaintext != encrypted
        assert isinstance(encrypted, str)

    def test_decrypt_invalid_data_raises(self, helper):
        with pytest.raises(InvalidToken):
            helper.decrypt("invalid-data")

    def test_user_specific_encrypt_decrypt_round_trip(self, helper):
        plaintext = "user-secret"
        salt = base64.urlsafe_b64encode(os.urandom(16)).decode()
        encrypted = helper.encrypt_for_user(plaintext, salt)
        decrypted = helper.decrypt_for_user(encrypted, salt)
        assert decrypted == plaintext
        assert plaintext != encrypted
        assert isinstance(encrypted, str)

    def test_user_specific_decrypt_with_wrong_salt_raises(self, helper):
        plaintext = "user-secret"
        salt1 = base64.urlsafe_b64encode(os.urandom(16)).decode()
        salt2 = base64.urlsafe_b64encode(os.urandom(16)).decode()
        encrypted = helper.encrypt_for_user(plaintext, salt1)
        with pytest.raises(InvalidToken):
            helper.decrypt_for_user(encrypted, salt2)

    def test_user_specific_decrypt_with_malformed_salt_raises(self, helper):
        plaintext = "user-secret"
        valid_salt = base64.urlsafe_b64encode(os.urandom(16)).decode()
        encrypted = helper.encrypt_for_user(plaintext, valid_salt)
        malformed_salt = "not-a-base64!!"
        with pytest.raises(Exception):  # could be ValueError or binascii.Error
            helper.decrypt_for_user(encrypted, malformed_salt)

    def test_init_with_missing_secret_key_raises(self):
        with pytest.raises(MissingEncryptionKeyError) as exc:
            FernetEncryptionHelper(secret_key=None)
        assert constants.ENCRYPTION_KEY_NOT_FOUND in str(exc.value)

    @pytest.mark.parametrize(
        "plaintext",
        ["", "a", " ", "\u2603", "0" * 10000],
        ids=[
            "empty string",
            "single char",
            "whitespace only",
            "unicode snowman",
            "very long string",
        ],
    )
    def test_encrypt_decrypt_varied_inputs(self, helper, plaintext):
        encrypted = helper.encrypt(plaintext)
        decrypted = helper.decrypt(encrypted)
        assert decrypted == plaintext

    @pytest.mark.parametrize(
        "plaintext",
        ["", "test123", "long" * 1000, "\u2603"],
        ids=["empty string", "short string", "very long string", "unicode snowman"],
    )
    def test_user_specific_encrypt_decrypt_varied_inputs(self, helper, plaintext):
        salt = base64.urlsafe_b64encode(os.urandom(16)).decode()
        encrypted = helper.encrypt_for_user(plaintext, salt)
        decrypted = helper.decrypt_for_user(encrypted, salt)
        assert decrypted == plaintext

    def test_helper_satisfies_protocol(self, helper: IEncryptionHelper):
        assert isinstance(helper, FernetEncryptionHelper)
        encrypted = helper.encrypt("test")
        assert isinstance(encrypted, str)
