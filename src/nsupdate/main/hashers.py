import hashlib

from django.contrib.auth.hashers import Argon2PasswordHasher, BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from django.utils.translation import gettext_lazy as _


class WeakArgon2PasswordHasher(Argon2PasswordHasher):
    """
    A relatively weak and fast Argon2 hasher.

    Takes ~1ms on a late 2020 AMD Ryzen 9 5950X.
    """
    algorithm = "weakargon2"
    library = "argon2"

    time_cost = 1
    memory_cost = 1024
    parallelism = 1


class SHA1PasswordHasher(BasePasswordHasher):
    """
    The SHA1 password hashing algorithm (re-implemented for Django 5.2 compatibility).
    """
    algorithm = "sha1"

    def encode(self, password, salt):
        self._check_encode_args(password, salt)
        hash_ = hashlib.sha1((salt + password).encode()).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash_)

    def decode(self, encoded):
        algorithm, salt, hash_ = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return {
            'algorithm': algorithm,
            'hash': hash_,
            'salt': salt,
        }

    def verify(self, password, encoded):
        decoded = self.decode(encoded)
        encoded_2 = self.encode(password, decoded['salt'])
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _('algorithm'): decoded['algorithm'],
            _('salt'): mask_hash(decoded['salt'], show=2),
            _('hash'): mask_hash(decoded['hash']),
        }

    def harden_runtime(self, password, encoded):
        pass
