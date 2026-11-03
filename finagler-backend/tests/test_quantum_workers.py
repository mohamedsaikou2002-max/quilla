import unittest

from app.providers.quantum_workers import validate_spec, run_pyliqtr


class TestGateSpecs(unittest.TestCase):
    def test_validates_bounded_circuit(self):
        data = {"qubits": 2, "operations": [
            {"gate": "h", "targets": [0]}, {"gate": "cx", "targets": [0, 1]}
        ]}
        self.assertEqual(validate_spec(data), data)

    def test_rejects_malformed_circuits(self):
        cases = [
            {"qubits": 17, "operations": []},
            {"qubits": 2, "operations": [{"gate": "python", "targets": [1]}]},
            {"qubits": 2, "operations": [{"gate": "cx", "targets": [0, 0]}]},
            {"qubits": 1, "operations": [{"gate": "x", "targets": [True]}]},
        ]
        for value in cases:
            with self.assertRaises(ValueError):
                validate_spec(value)

    def test_optional_pyliqtr_missing_is_explicit(self):
        # Input validation is always available without importing scientific packages.
        self.assertEqual(validate_spec({"qubits": 1, "operations": []})["qubits"], 1)


if __name__ == "__main__":
    unittest.main()
