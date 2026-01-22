#!/usr/bin/env python3
"""Tests for Declaration validation."""

import unittest
from datetime import date
from decimal import Decimal

from Modelo720 import DeclarationValidationError
from Modelo720.declaracion import (
    Header720,
    Detalle720,
    Declaration,
    Valoracion,
    ClaveBien,
    Origen,
)


class TestDeclarationValidation(unittest.TestCase):
    """Test Declaration validation methods."""

    def setUp(self):
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
            numero_identificativo="7201234567890",
            declaracion_complementaria=False,
            declaracion_sustitutiva=False,
            numero_identificativo_anterior=None,
            numero_total_registros=1,
            suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("1000.00")),
            suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0.00")),
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
            clave_tipo_bien=ClaveBien.C,
            subclave=1,
            tipo_derecho_real_inmueble="",
            codigo_pais="US",
            clave_identificacion=0,
            identificacion_valores="",
            clave_ident_cuenta="I",
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
            valoracion_1=Valoracion(signo=" ", importe=Decimal("1000.00")),
            valoracion_2=Valoracion(signo=" ", importe=Decimal("0.00")),
            clave_repr_valores="",
            numero_valores_entera=0,
            numero_valores_decimal=0,
            clave_tipo_bien_inmueble="",
            porcentaje_participacion_entera=100,
            porcentaje_participacion_decimal=0,
        )

        self.declaration = Declaration(header=self.header, detalles=[self.detalle])

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
        # Test record count mismatch
        self.header.numero_total_registros = 5
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("no concuerda con el número de detalles", str(cm.exception))

    def test_validate_business_rules(self):
        """Test business rule validation."""
        # Test subclave rule for clave I
        self.header.numero_total_registros = 1
        self.detalle.clave_tipo_bien = ClaveBien.I
        self.detalle.subclave = 1
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("subclave must be 0", str(cm.exception))

    def test_validate_raises_exception(self):
        """Test validate raises exception on errors."""
        self.header.numero_total_registros = 10
        with self.assertRaises(DeclarationValidationError) as cm:
            self.declaration.validate()
        self.assertIn("no concuerda con el número de detalles", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
