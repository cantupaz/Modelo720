#!/usr/bin/env python3
"""Tests for NIF/NIE validation."""

import unittest
from Modelo720 import validar_nif


class TestNIFValidation(unittest.TestCase):
    """Test NIF/NIE validation function."""

    def test_valid_dni(self):
        """Test valid DNI formats."""
        # Calculate valid DNIs
        self.assertTrue(validar_nif("12345678Z"))
        self.assertTrue(validar_nif("87654321X"))

    def test_valid_nie(self):
        """Test valid NIE formats."""
        self.assertTrue(validar_nif("X1234567L"))
        self.assertTrue(validar_nif("Y9876543F"))
        self.assertTrue(validar_nif("Z0123456P"))

    def test_invalid_nif_wrong_letter(self):
        """Test invalid NIF with wrong control letter."""
        self.assertFalse(validar_nif("12345678A"))
        self.assertFalse(validar_nif("87654321Y"))

    def test_invalid_nif_format(self):
        """Test invalid NIF formats."""
        self.assertFalse(validar_nif(""))
        self.assertFalse(validar_nif("1234567"))
        self.assertFalse(validar_nif("123456789"))
        self.assertFalse(validar_nif("ABCDEFGHI"))

    def test_nif_case_insensitive(self):
        """Test NIF validation is case-insensitive."""
        self.assertTrue(validar_nif("12345678z"))
        self.assertTrue(validar_nif("x1234567l"))


if __name__ == "__main__":
    unittest.main()
