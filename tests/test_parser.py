#!/usr/bin/env python3
"""Tests for Parser class and field specifications."""

import unittest
from datetime import date
from decimal import Decimal

from Modelo720 import Parser, Valoracion
from Modelo720.parser import FieldSpec, HEADER_FIELDS, DETALLE_FIELDS
from Modelo720.declaracion import ClaveBien, Origen


class TestFieldSpec(unittest.TestCase):
    """Test FieldSpec definitions and consistency."""

    def test_header_field_order_preserved(self):
        """Test that header field order matches expected CSV order."""
        expected_order = [
            "tipo_registro",
            "modelo",
            "ejercicio",
            "nif_declarante",
            "nombre_razon",
            "tipo_soporte",
            "telefono_contacto",
            "persona_contacto",
            "numero_identificativo",
            "declaracion_complementaria",
            "declaracion_sustitutiva",
            "numero_identificativo_anterior",
            "numero_total_registros",
            "suma_valoracion_1",
            "suma_valoracion_2",
        ]
        actual_order = [f.name for f in HEADER_FIELDS]
        self.assertEqual(actual_order, expected_order)

    def test_detalle_field_order_preserved(self):
        """Test that detalle field order matches expected CSV order."""
        expected_order = [
            "tipo_registro",
            "modelo",
            "ejercicio",
            "nif_declarante",
            "nif_declarado",
            "nif_representante",
            "nombre_razon_declarado",
            "clave_condicion",
            "tipo_titularidad_texto",
            "clave_tipo_bien",
            "subclave",
            "tipo_derecho_real_inmueble",
            "codigo_pais",
            "clave_identificacion",
            "identificacion_valores",
            "clave_ident_cuenta",
            "codigo_bic",
            "codigo_cuenta",
            "identificacion_entidad",
            "nif_entidad_pais_residencia",
            "domicilio_via_num",
            "domicilio_complemento",
            "domicilio_poblacion",
            "domicilio_region",
            "domicilio_cp",
            "domicilio_pais",
            "fecha_incorporacion",
            "origen",
            "fecha_extincion",
            "valoracion_1",
            "valoracion_2",
            "clave_repr_valores",
            "numero_valores_entera",
            "numero_valores_decimal",
            "clave_tipo_bien_inmueble",
            "porcentaje_participacion_entera",
            "porcentaje_participacion_decimal",
        ]
        actual_order = [f.name for f in DETALLE_FIELDS]
        self.assertEqual(actual_order, expected_order)

    def test_field_positions_no_overlaps(self):
        """Test that field positions don't overlap."""
        for fields, name in [(HEADER_FIELDS, "HEADER"), (DETALLE_FIELDS, "DETALLE")]:
            positions = set()
            for f in fields:
                field_positions = set(range(f.start, f.end + 1))
                overlap = positions & field_positions
                if overlap:
                    self.fail(
                        f"{name} field '{f.name}' overlaps at positions {sorted(overlap)}"
                    )
                positions.update(field_positions)


class TestParsingHelpers(unittest.TestCase):
    """Test parsing helper methods in Parser class."""

    def setUp(self):
        self.parser = Parser()

    def test_to_date8_valid(self):
        """Test date parsing with valid input."""
        result = self.parser._to_date8("20240315")
        self.assertEqual(result, date(2024, 3, 15))

    def test_to_date8_empty(self):
        """Test date parsing with empty input."""
        self.assertIsNone(self.parser._to_date8(""))
        self.assertIsNone(self.parser._to_date8("   "))
        self.assertIsNone(self.parser._to_date8("00000000"))

    def test_to_date8_invalid(self):
        """Test date parsing with invalid input."""
        with self.assertRaises(ValueError):
            self.parser._to_date8("abcd1234")
        with self.assertRaises(ValueError):
            self.parser._to_date8("123")

    def test_to_int_valid(self):
        """Test integer parsing with valid input."""
        self.assertEqual(self.parser._to_int("123"), 123)
        self.assertEqual(self.parser._to_int("  456  "), 456)
        self.assertEqual(self.parser._to_int(""), 0)

    def test_to_int_invalid(self):
        """Test integer parsing with invalid input."""
        with self.assertRaises(ValueError):
            self.parser._to_int("abc")
        with self.assertRaises(ValueError):
            self.parser._to_int("12.34")

    def test_to_decimal_from_cents(self):
        """Test decimal conversion from cents."""
        result = self.parser._to_decimal_from_cents(" ", "123456")
        self.assertEqual(result, Decimal("1234.56"))

        result = self.parser._to_decimal_from_cents("N", "789000")
        self.assertEqual(result, Decimal("-7890.00"))

        result = self.parser._to_decimal_from_cents(" ", "")
        self.assertEqual(result, Decimal("0.00"))


class TestFieldParsing(unittest.TestCase):
    """Test field parsing using FieldSpec."""

    def setUp(self):
        self.parser = Parser()

    def test_parse_field_str(self):
        """Test string field parsing."""
        field_spec = FieldSpec("test_field", 1, 10, "str")
        result = self.parser._parse_field("Hello     ", field_spec)
        self.assertEqual(result, "Hello")

        # Test empty string handling
        field_spec_optional = FieldSpec("test_field", 1, 10, "str")
        result = self.parser._parse_field("          ", field_spec_optional)
        self.assertEqual(result, "")

    def test_parse_field_enum(self):
        """Test enum field parsing."""
        field_spec = FieldSpec("clave_bien", 1, 1, "enum", enum_class=ClaveBien)
        result = self.parser._parse_field("C", field_spec)
        self.assertEqual(result, ClaveBien.C)

    def test_parse_field_valoracion(self):
        """Test valoracion field parsing."""
        field_spec = FieldSpec("valor", 1, 18, "valoracion")  # 1 char sign + 17 digits
        result = self.parser._parse_field(" 00000001234567890", field_spec)
        self.assertIsInstance(result, Valoracion)
        self.assertEqual(result.signo, " ")
        self.assertEqual(result.importe, Decimal("12345678.90"))


class TestCSVRoundTrip(unittest.TestCase):
    """Test CSV reading and writing."""

    def setUp(self):
        self.parser = Parser()

        # Create minimal test data
        self.csv_content = """__SECTION__,HEADER
field,value
tipo_registro,1
modelo,720
ejercicio,2024
nif_declarante,Y9127527Z
nombre_razon,TEST USER
tipo_soporte,T
numero_identificativo,7201234567890
declaracion_complementaria,0
declaracion_sustitutiva,0
numero_total_registros,1
suma_valoracion_1,1000.00
suma_valoracion_2,0.00
__SECTION__,DETALLES
tipo_registro,modelo,ejercicio,nif_declarante,nif_declarado,nif_representante,nombre_razon_declarado,clave_condicion,tipo_titularidad_texto,clave_tipo_bien,subclave,tipo_derecho_real_inmueble,codigo_pais,clave_identificacion,identificacion_valores,clave_ident_cuenta,codigo_bic,codigo_cuenta,identificacion_entidad,nif_entidad_pais_residencia,domicilio_via_num,domicilio_complemento,domicilio_poblacion,domicilio_region,domicilio_cp,domicilio_pais,fecha_incorporacion,origen,fecha_extincion,valoracion_1,valoracion_2,clave_repr_valores,numero_valores_entera,numero_valores_decimal,clave_tipo_bien_inmueble,porcentaje_participacion_entera,porcentaje_participacion_decimal
2,720,2024,Y9127527Z,Y9127527Z,,TEST USER,1,,C,1,,US,0,,,,,BANCO TEST,,,,,,,US,2024-01-01,A,,1000.00,0.00,,0,0,,100,0
"""

    def test_csv_read_basic(self):
        """Test basic CSV reading."""
        # Write test content to temporary file
        with open("temp_test.csv", "w", encoding="utf-8") as f:
            f.write(self.csv_content)

        try:
            declaration = self.parser.read_csv("temp_test.csv")
        finally:
            # Clean up temp file
            import os

            if os.path.exists("temp_test.csv"):
                os.remove("temp_test.csv")

        self.assertEqual(declaration.header.nif_declarante, "Y9127527Z")
        self.assertEqual(declaration.header.ejercicio, 2024)
        self.assertEqual(len(declaration.detalles), 1)
        self.assertEqual(declaration.detalles[0].clave_tipo_bien, ClaveBien.C)


if __name__ == "__main__":
    unittest.main()
