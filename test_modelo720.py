#!/usr/bin/env python3
"""
Unit tests for Modelo720 parser refactoring.
Tests field specifications, parsing helpers, and edge cases.
"""
import unittest
from datetime import date
from decimal import Decimal
from io import StringIO

from Modelo720 import Modelo720, Valoracion, DeclarationValidationError, Modelo720FormatError, CSV720Error
from Modelo720.modelo720 import FieldSpec, HEADER_FIELDS, DETALLE_FIELDS
from Modelo720.declaracion import ClaveBien, Origen

class TestFieldSpec(unittest.TestCase):
    """Test FieldSpec definitions and consistency."""
    
    def test_header_field_order_preserved(self):
        """Test that header field order matches expected CSV order."""
        expected_order = [
            "tipo_registro", "modelo", "ejercicio", "nif_declarante", "nombre_razon",
            "tipo_soporte", "telefono_contacto", "persona_contacto", "numero_identificativo",
            "declaracion_complementaria", "declaracion_sustitutiva", "numero_identificativo_anterior",
            "numero_total_registros", "suma_valoracion_1", "suma_valoracion_2"
        ]
        actual_order = [f.name for f in HEADER_FIELDS if f.csv_include]
        self.assertEqual(actual_order, expected_order)
    
    def test_detalle_field_order_preserved(self):
        """Test that detalle field order matches expected CSV order."""
        expected_order = [
            "tipo_registro", "modelo", "ejercicio", "nif_declarante", "nif_declarado", "nif_representante",
            "nombre_razon_declarado", "clave_condicion", "tipo_titularidad_texto", "clave_tipo_bien", "subclave",
            "tipo_derecho_real_inmueble", "codigo_pais", "clave_identificacion", "identificacion_valores",
            "clave_ident_cuenta", "codigo_bic", "codigo_cuenta", "identificacion_entidad", "nif_entidad_pais_residencia",
            "domicilio_via_num", "domicilio_complemento", "domicilio_poblacion", "domicilio_region", "domicilio_cp",
            "domicilio_pais", "fecha_incorporacion", "origen", "fecha_extincion", "valoracion_1", "valoracion_2",
            "clave_repr_valores", "numero_valores_entera", "numero_valores_decimal", "clave_tipo_bien_inmueble",
            "porcentaje_participacion_entera", "porcentaje_participacion_decimal"
        ]
        actual_order = [f.name for f in DETALLE_FIELDS if f.csv_include]
        self.assertEqual(actual_order, expected_order)
    
    def test_field_positions_no_overlaps(self):
        """Test that field positions don't overlap."""
        for fields, name in [(HEADER_FIELDS, "HEADER"), (DETALLE_FIELDS, "DETALLE")]:
            positions = set()
            for f in fields:
                field_positions = set(range(f.start, f.end + 1))
                overlap = positions & field_positions
                if overlap:
                    self.fail(f"{name} field '{f.name}' overlaps at positions {sorted(overlap)}")
                positions.update(field_positions)

class TestParsingHelpers(unittest.TestCase):
    """Test parsing helper methods in Modelo720 class."""
    
    def setUp(self):
        self.parser = Modelo720()
    
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
        self.parser = Modelo720()
    
    def test_parse_field_str(self):
        """Test string field parsing."""
        field_spec = FieldSpec("test_field", 1, 10, "str")
        result = self.parser._parse_field("Hello     ", field_spec)
        self.assertEqual(result, "Hello")
        
        # Test empty string handling (non-required field)
        field_spec_optional = FieldSpec("test_field", 1, 10, "str", required=False)
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

class TestDeclarationValidation(unittest.TestCase):
    """Test Declaration validation methods."""
    
    def setUp(self):
        from datetime import date
        from Modelo720.modelo720 import Header720, Detalle720, Declaration, Valoracion
        
        # Create a minimal valid declaration for testing
        self.header = Header720(
            tipo_registro=1,
            modelo="720",
            ejercicio=2024,
            nif_declarante="Y9127527Z",
            nombre_razon="TEST USER",
            tipo_soporte="T",
            telefono_contacto=None,
            persona_contacto=None,
            numero_identificativo="1234567890123",
            declaracion_complementaria=False,
            declaracion_sustitutiva=False,
            numero_identificativo_anterior=None,
            numero_total_registros=1,
            suma_valoracion_1=Valoracion(" ", Decimal("1000.00")),
            suma_valoracion_2=Valoracion(" ", Decimal("0.00")),
        )
        
        self.detalle = Detalle720(
            tipo_registro=2,
            modelo="720",
            ejercicio=2024,
            nif_declarante="Y9127527Z",
            nif_declarado="Y9127527Z",
            nif_representante="",
            nombre_razon_declarado="TEST USER",
            clave_condicion=1,
            tipo_titularidad_texto="",
            clave_tipo_bien=ClaveBien.V,
            subclave=0,
            tipo_derecho_real_inmueble="",
            codigo_pais="US",
            clave_identificacion=1,
            identificacion_valores="",
            clave_ident_cuenta="",
            codigo_bic="",
            codigo_cuenta="",
            identificacion_entidad="",
            nif_entidad_pais_residencia="",
            domicilio_via_num="",
            domicilio_complemento="",
            domicilio_poblacion="",
            domicilio_region="",
            domicilio_cp="",
            domicilio_pais="US",
            fecha_incorporacion=date(2024, 1, 1),
            origen=Origen.A,
            fecha_extincion=None,
            valoracion_1=Valoracion(" ", Decimal("1000.00")),
            valoracion_2=Valoracion(" ", Decimal("0.00")),
            clave_repr_valores="",
            numero_valores_entera=0,
            numero_valores_decimal=0,
            clave_tipo_bien_inmueble="",
            porcentaje_participacion_entera=100,
            porcentaje_participacion_decimal=0,
        )
        
        self.declaration = Declaration(self.header, [self.detalle])
    
    def test_validate_basic_success(self):
        """Test basic validation passes for valid declaration."""
        try:
            self.declaration.validate()
        except DeclarationValidationError:
            self.fail("validate() raised DeclarationValidationError unexpectedly")
    
    def test_validate_strict_success(self):
        """Test validation passes for valid declaration."""
        try:
            self.declaration.validate()
        except DeclarationValidationError:
            self.fail("validate() raised DeclarationValidationError unexpectedly")
    
    def test_validate_structure_failures(self):
        """Test structural validation catches basic errors."""
        # Test wrong tipo_registro
        self.header.tipo_registro = 2
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("Header tipo_registro must be 1", str(cm.exception))
        
        # Test wrong modelo
        self.header.tipo_registro = 1
        self.header.modelo = "730"
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("Modelo must be 720", str(cm.exception))
        
        # Test record count mismatch
        self.header.modelo = "720"
        self.header.numero_total_registros = 5
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("does not match detail count", str(cm.exception))
    
    def test_validate_business_rules(self):
        """Test business rule validation."""
        # Test invalid NIF format
        self.header.numero_identificativo = "123"
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("Header numero_identificativo must be 13 digits", str(cm.exception))
        
        # Test subclave rule for clave I
        self.header.numero_identificativo = "1234567890123"
        self.detalle.clave_tipo_bien = ClaveBien.I
        self.detalle.subclave = 1
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("Detail 1: subclave must be 0 for clave 'I'", str(cm.exception))
    
    def test_validate_raises_exception(self):
        """Test validate raises exception on errors."""
        self.header.tipo_registro = 2
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("Header tipo_registro must be 1", str(cm.exception))



class TestCSVRoundTrip(unittest.TestCase):
    """Test CSV reading and writing."""
    
    def setUp(self):
        self.parser = Modelo720()
        
        # Create minimal test data
        self.csv_content = '''__SECTION__,HEADER
field,value
tipo_registro,1
modelo,720
ejercicio,2024
nif_declarante,Y9127527Z
nombre_razon,TEST USER
tipo_soporte,T
numero_identificativo,1234567890123
declaracion_complementaria,0
declaracion_sustitutiva,0
numero_total_registros,1
suma_valoracion_1,1000.00
suma_valoracion_2,0.00
__SECTION__,DETALLES
tipo_registro,modelo,ejercicio,nif_declarante,nif_declarado,nif_representante,nombre_razon_declarado,clave_condicion,tipo_titularidad_texto,clave_tipo_bien,subclave,tipo_derecho_real_inmueble,codigo_pais,clave_identificacion,identificacion_valores,clave_ident_cuenta,codigo_bic,codigo_cuenta,identificacion_entidad,nif_entidad_pais_residencia,domicilio_via_num,domicilio_complemento,domicilio_poblacion,domicilio_region,domicilio_cp,domicilio_pais,fecha_incorporacion,origen,fecha_extincion,valoracion_1,valoracion_2,clave_repr_valores,numero_valores_entera,numero_valores_decimal,clave_tipo_bien_inmueble,porcentaje_participacion_entera,porcentaje_participacion_decimal
2,720,2024,Y9127527Z,Y9127527Z,,TEST USER,1,,V,0,,US,1,,,,,,,,,,,,US,2024-01-01,A,,1000.00,0.00,,0,0,,100,0
'''
    
    def test_csv_read_basic(self):
        """Test basic CSV reading."""
        csv_file = StringIO(self.csv_content)
        declaration = self.parser.read_csv(csv_file)
        
        self.assertEqual(declaration.header.nif_declarante, "Y9127527Z")
        self.assertEqual(declaration.header.ejercicio, 2024)
        self.assertEqual(len(declaration.detalles), 1)
        self.assertEqual(declaration.detalles[0].clave_tipo_bien, ClaveBien.V)

if __name__ == '__main__':
    unittest.main()