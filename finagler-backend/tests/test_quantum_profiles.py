"""Pure-Python unit tests for the externally computed quantum profile adapter."""
import unittest

from app.providers.quantum_profiles import compare_profiles, normalize_profile


PROFILE = {
    "provider": "pyliqtr",
    "algorithm": "synthetic-algorithm-1",
    "upstream_version": "research-test",
    "logical_qubits": 8,
    "t_count": 600,
    "t_depth": 60,
}


class TestProfiles(unittest.TestCase):
    def test_normalizes_without_falsely_claiming_verification(self):
        p = normalize_profile(PROFILE)
        self.assertEqual(p["t_count"], 600)
        self.assertFalse(p["verified"])

    def test_compares_like_algorithm(self):
        b = dict(PROFILE, provider="benchq", logical_qubits=10, t_count=500)
        self.assertEqual(compare_profiles(PROFILE, b)["delta"]["t_count"], -100)

    def test_rejects_incompatible_algorithm(self):
        with self.assertRaises(ValueError):
            compare_profiles(PROFILE, dict(PROFILE, algorithm="different"))

    def test_rejects_impossible_count_and_unknown_provider(self):
        with self.assertRaises(ValueError):
            normalize_profile(dict(PROFILE, t_depth=700))
        with self.assertRaises(ValueError):
            normalize_profile(dict(PROFILE, provider="unrecognized"))
        with self.assertRaises(ValueError):
            normalize_profile(dict(PROFILE, logical_qubits=True))


if __name__ == "__main__":
    unittest.main()
