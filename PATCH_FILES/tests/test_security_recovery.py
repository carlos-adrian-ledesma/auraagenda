import unittest
from app.services.network_guard import canonical_trusted_networks
from app.services.privacy import (
    AttemptLimiter,
    generate_master_key,
    make_master_hash,
    validate_new_pin,
    verify_master_key,
)
from tests.common import temp_db


class SecurityRecoveryTests(unittest.TestCase):
    def test_master_key_is_high_entropy_and_only_hash_is_verifiable(self):
        key = generate_master_key()
        self.assertGreaterEqual(len(key.replace('-', '')), 64)
        digest, salt = make_master_hash(key)
        self.assertNotIn(key.replace('-', ''), digest)
        self.assertTrue(verify_master_key(key, digest, salt))
        self.assertFalse(verify_master_key(generate_master_key(), digest, salt))

    def test_new_pin_policy_is_six_or_more(self):
        self.assertFalse(validate_new_pin('1234')[0])
        self.assertTrue(validate_new_pin('123456')[0])

    def test_attempt_limiter_progressively_delays(self):
        limiter = AttemptLimiter()
        self.assertEqual(limiter.register_failure(now=10), 0)
        self.assertEqual(limiter.register_failure(now=10), 0)
        self.assertGreaterEqual(limiter.register_failure(now=10), 2)
        self.assertGreater(limiter.remaining_seconds(now=10), 0)
        limiter.register_success()
        self.assertEqual(limiter.remaining_seconds(now=10), 0)

    def test_network_cidr_is_canonical(self):
        self.assertEqual(canonical_trusted_networks('192.168.1.12'), '192.168.1.12/32')
        self.assertEqual(canonical_trusted_networks('10.0.0.55/24'), '10.0.0.0/24')
        with self.assertRaises(ValueError):
            canonical_trusted_networks('not-an-ip')

    def test_installation_id_is_unique_and_persisted(self):
        from app.services.recovery import RecoveryService

        td, db = temp_db()
        self.addCleanup(td.cleanup)
        service = RecoveryService(db)
        first = service.ensure_installation_id()
        second = service.ensure_installation_id()
        self.assertEqual(first, second)
        self.assertGreater(len(first), 20)


if __name__ == '__main__':
    unittest.main()
