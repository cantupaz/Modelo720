#!/usr/bin/env python3
"""Tests for Pydantic models (Valoracion, Header720, Detalle720)."""

import unittest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError

from Modelo720 import Valoracion
from Modelo720.declaracion import Header720, Detalle720, ClaveBien, Origen


class TestValoracionModel(unittest.TestCase):
    """Test Valoracion model validation."""

    def test_valoracion_valid_positive(self):
        """Test valid positive valoracion."""
        val = Valoracion(signo=" ", importe=Decimal("1234.56"))
        self.assertEqual(val.signo, " ")
        self.assertEqual(val.importe, Decimal("1234.56"))

    def test_valoracion_valid_negative(self):
        """Test valid negative valoracion."""
        val = Valoracion(signo="N", importe=Decimal("1234.56"))
        self.assertEqual(val.signo, "N")
        self.assertEqual(val.importe, Decimal("1234.56"))

    def test_valoracion_invalid_signo(self):
        """Test invalid signo raises error."""
        with self.assertRaises(ValidationError):
            Valoracion(signo="X", importe=Decimal("1234.56"))

        with self.assertRaises(ValidationError):
            Valoracion(signo="+", importe=Decimal("1234.56"))


class TestHeader720Validation(unittest.TestCase):
    """Test Header720 model validation rules."""

    def create_valid_header(self):
        """Helper to create a valid header."""
        return Header720(
            tipo_registro=1,
            modelo="720",
            ejercicio=2024,
            nif_declarante="12345678Z",
            nombre_razon="Juan Perez Garcia",
            tipo_soporte="T",
            numero_identificativo="7201234567890",
            declaracion_complementaria=False,
            declaracion_sustitutiva=False,
            numero_total_registros=1,
            suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("1000.00")),
            suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0.00")),
        )

    def test_header_valid(self):
        """Test valid header creation."""
        header = self.create_valid_header()
        self.assertEqual(header.tipo_registro, 1)
        self.assertEqual(header.modelo, "720")

    def test_header_invalid_tipo_registro(self):
        """Test tipo_registro must be 1."""
        with self.assertRaises(ValidationError):
            Header720(
                tipo_registro=2,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nombre_razon="Test",
                tipo_soporte="T",
                numero_identificativo="7201234567890",
                declaracion_complementaria=False,
                declaracion_sustitutiva=False,
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )

    def test_header_invalid_modelo(self):
        """Test modelo must be 720."""
        with self.assertRaises(ValidationError) as cm:
            Header720(
                tipo_registro=1,
                modelo="730",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nombre_razon="Test",
                tipo_soporte="T",
                numero_identificativo="7201234567890",
                declaracion_complementaria=False,
                declaracion_sustitutiva=False,
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )
        self.assertIn("720", str(cm.exception))

    def test_header_invalid_nif(self):
        """Test NIF validation."""
        with self.assertRaises(ValidationError):
            Header720(
                tipo_registro=1,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678A",  # Wrong control letter
                nombre_razon="Test",
                tipo_soporte="T",
                numero_identificativo="7201234567890",
                declaracion_complementaria=False,
                declaracion_sustitutiva=False,
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )

    def test_header_invalid_tipo_soporte(self):
        """Test tipo_soporte must be T."""
        with self.assertRaises(ValidationError):
            Header720(
                tipo_registro=1,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nombre_razon="Test",
                tipo_soporte="X",
                numero_identificativo="7201234567890",
                declaracion_complementaria=False,
                declaracion_sustitutiva=False,
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )

    def test_header_numero_identificativo_starts_with_720(self):
        """Test numero_identificativo must start with 720."""
        with self.assertRaises(ValidationError) as cm:
            Header720(
                tipo_registro=1,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nombre_razon="Test",
                tipo_soporte="T",
                numero_identificativo="7301234567890",
                declaracion_complementaria=False,
                declaracion_sustitutiva=False,
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )
        self.assertIn("720", str(cm.exception))

    def test_header_complementaria_requires_anterior(self):
        """Test declaracion_complementaria requires numero_identificativo_anterior."""
        with self.assertRaises(ValidationError):
            Header720(
                tipo_registro=1,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nombre_razon="Test",
                tipo_soporte="T",
                numero_identificativo="7201234567890",
                declaracion_complementaria=True,
                declaracion_sustitutiva=False,
                numero_identificativo_anterior=None,
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )

    def test_header_both_complementaria_and_sustitutiva(self):
        """Test cannot be both complementaria and sustitutiva."""
        with self.assertRaises(ValidationError):
            Header720(
                tipo_registro=1,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nombre_razon="Test",
                tipo_soporte="T",
                numero_identificativo="7201234567890",
                declaracion_complementaria=True,
                declaracion_sustitutiva=True,
                numero_identificativo_anterior="7201234567889",
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )

    def test_header_max_length_constraints(self):
        """Test field length constraints."""
        with self.assertRaises(ValidationError):
            Header720(
                tipo_registro=1,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nombre_razon="A" * 50,  # Exceeds 40 chars
                tipo_soporte="T",
                numero_identificativo="7201234567890",
                declaracion_complementaria=False,
                declaracion_sustitutiva=False,
                numero_total_registros=1,
                suma_valoracion_1=Valoracion(signo=" ", importe=Decimal("0")),
                suma_valoracion_2=Valoracion(signo=" ", importe=Decimal("0")),
            )


class TestDetalle720Validation(unittest.TestCase):
    """Test Detalle720 model validation rules."""

    def create_valid_detalle(self, clave_tipo_bien=ClaveBien.C, subclave=1):
        """Helper to create a valid detalle."""
        return Detalle720(
            tipo_registro=2,
            modelo="720",
            ejercicio=2024,
            nif_declarante="12345678Z",
            nif_declarado="12345678Z",
            nif_representante="",
            nombre_razon_declarado="Juan Perez Garcia",
            clave_condicion=1,
            tipo_titularidad_texto="",
            clave_tipo_bien=clave_tipo_bien,
            subclave=subclave,
            tipo_derecho_real_inmueble="",
            codigo_pais="US",
            clave_identificacion=0,
            identificacion_valores="",
            clave_ident_cuenta="I" if clave_tipo_bien == ClaveBien.C else "",
            codigo_bic="",
            codigo_cuenta="",
            identificacion_entidad="BANCO TEST",
            nif_entidad_pais_residencia="",
            domicilio_via_num="Main St 123",
            domicilio_complemento="",
            domicilio_poblacion="New York",
            domicilio_region="NY",
            domicilio_cp="10001",
            domicilio_pais="US",
            fecha_incorporacion=date(2024, 1, 1),
            origen=Origen.A,
            fecha_extincion=None,
            valoracion_1=Valoracion(signo=" ", importe=Decimal("10000.00")),
            valoracion_2=Valoracion(signo=" ", importe=Decimal("9500.00")),
            clave_repr_valores="",
            numero_valores_entera=0,
            numero_valores_decimal=0,
            clave_tipo_bien_inmueble="",
            porcentaje_participacion_entera=100,
            porcentaje_participacion_decimal=0,
        )

    def test_detalle_valid_bank_account(self):
        """Test valid bank account detalle."""
        detalle = self.create_valid_detalle(ClaveBien.C, 1)
        self.assertEqual(detalle.clave_tipo_bien, ClaveBien.C)
        self.assertEqual(detalle.subclave, 1)

    def test_detalle_invalid_subclave_for_I(self):
        """Test subclave must be 0 for clave_tipo_bien I."""
        with self.assertRaises(ValidationError):
            self.create_valid_detalle(ClaveBien.I, 1)

    def test_detalle_invalid_subclave_for_C(self):
        """Test subclave must be 1-5 for clave_tipo_bien C."""
        with self.assertRaises(ValidationError):
            self.create_valid_detalle(ClaveBien.C, 6)

    def test_detalle_invalid_subclave_for_V(self):
        """Test subclave must be 1-3 for clave_tipo_bien V."""
        # Create a valid V detalle with subclave 1 first
        valid_detalle = Detalle720(
            tipo_registro=2,
            modelo="720",
            ejercicio=2024,
            nif_declarante="12345678Z",
            nif_declarado="12345678Z",
            nif_representante="",
            nombre_razon_declarado="Juan Perez Garcia",
            clave_condicion=1,
            tipo_titularidad_texto="",
            clave_tipo_bien=ClaveBien.V,
            subclave=1,
            tipo_derecho_real_inmueble="",
            codigo_pais="US",
            clave_identificacion=1,
            identificacion_valores="US1234567890",
            clave_ident_cuenta="",
            codigo_bic="",
            codigo_cuenta="",
            identificacion_entidad="Test Entity",
            nif_entidad_pais_residencia="",
            domicilio_via_num="Main St 123",
            domicilio_complemento="",
            domicilio_poblacion="New York",
            domicilio_region="NY",
            domicilio_cp="10001",
            domicilio_pais="US",
            fecha_incorporacion=date(2024, 1, 1),
            origen=Origen.A,
            fecha_extincion=None,
            valoracion_1=Valoracion(signo=" ", importe=Decimal("10000.00")),
            valoracion_2=Valoracion(signo=" ", importe=Decimal("0.00")),
            clave_repr_valores="A",
            numero_valores_entera=100,
            numero_valores_decimal=0,
            clave_tipo_bien_inmueble="",
            porcentaje_participacion_entera=100,
            porcentaje_participacion_decimal=0,
        )
        # Now try with invalid subclave
        detalle_data = valid_detalle.__dict__.copy()
        detalle_data["subclave"] = 4
        with self.assertRaises(ValidationError):
            Detalle720(**detalle_data)

    def test_detalle_clave_condicion_range(self):
        """Test clave_condicion must be 1-8."""
        detalle_data = self.create_valid_detalle().__dict__
        detalle_data["clave_condicion"] = 0
        with self.assertRaises(ValidationError):
            Detalle720(**detalle_data)

        detalle_data["clave_condicion"] = 9
        with self.assertRaises(ValidationError):
            Detalle720(**detalle_data)

    def test_detalle_origen_C_requires_fecha_extincion(self):
        """Test origen C requires fecha_extincion."""
        detalle_data = self.create_valid_detalle().__dict__
        detalle_data["origen"] = Origen.C
        detalle_data["fecha_extincion"] = None
        with self.assertRaises(ValidationError):
            Detalle720(**detalle_data)

    def test_detalle_clave_identificacion_for_V(self):
        """Test clave_identificacion required for V."""
        # Create a fully valid V detalle
        detalle = Detalle720(
            tipo_registro=2,
            modelo="720",
            ejercicio=2024,
            nif_declarante="12345678Z",
            nif_declarado="12345678Z",
            nif_representante="",
            nombre_razon_declarado="Juan Perez Garcia",
            clave_condicion=1,
            tipo_titularidad_texto="",
            clave_tipo_bien=ClaveBien.V,
            subclave=1,
            tipo_derecho_real_inmueble="",
            codigo_pais="US",
            clave_identificacion=1,
            identificacion_valores="US1234567890",
            clave_ident_cuenta="",
            codigo_bic="",
            codigo_cuenta="",
            identificacion_entidad="Test Entity",
            nif_entidad_pais_residencia="",
            domicilio_via_num="Main St 123",
            domicilio_complemento="",
            domicilio_poblacion="New York",
            domicilio_region="NY",
            domicilio_cp="10001",
            domicilio_pais="US",
            fecha_incorporacion=date(2024, 1, 1),
            origen=Origen.A,
            fecha_extincion=None,
            valoracion_1=Valoracion(signo=" ", importe=Decimal("10000.00")),
            valoracion_2=Valoracion(signo=" ", importe=Decimal("0.00")),
            clave_repr_valores="A",
            numero_valores_entera=100,
            numero_valores_decimal=0,
            clave_tipo_bien_inmueble="",
            porcentaje_participacion_entera=100,
            porcentaje_participacion_decimal=0,
        )
        self.assertEqual(detalle.clave_identificacion, 1)

    def test_detalle_identificacion_valores_for_V(self):
        """Test identificacion_valores required for V."""
        # Try to create V detalle with empty identificacion_valores
        with self.assertRaises(ValidationError):
            Detalle720(
                tipo_registro=2,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nif_declarado="12345678Z",
                nif_representante="",
                nombre_razon_declarado="Juan Perez Garcia",
                clave_condicion=1,
                tipo_titularidad_texto="",
                clave_tipo_bien=ClaveBien.V,
                subclave=1,
                tipo_derecho_real_inmueble="",
                codigo_pais="US",
                clave_identificacion=1,
                identificacion_valores="",  # Empty - should fail
                clave_ident_cuenta="",
                codigo_bic="",
                codigo_cuenta="",
                identificacion_entidad="Test Entity",
                nif_entidad_pais_residencia="",
                domicilio_via_num="Main St 123",
                domicilio_complemento="",
                domicilio_poblacion="New York",
                domicilio_region="NY",
                domicilio_cp="10001",
                domicilio_pais="US",
                fecha_incorporacion=date(2024, 1, 1),
                origen=Origen.A,
                fecha_extincion=None,
                valoracion_1=Valoracion(signo=" ", importe=Decimal("10000.00")),
                valoracion_2=Valoracion(signo=" ", importe=Decimal("0.00")),
                clave_repr_valores="A",
                numero_valores_entera=100,
                numero_valores_decimal=0,
                clave_tipo_bien_inmueble="",
                porcentaje_participacion_entera=100,
                porcentaje_participacion_decimal=0,
            )

    def test_detalle_real_estate_requires_tipo(self):
        """Test real estate requires clave_tipo_bien_inmueble."""
        # Try to create B detalle without clave_tipo_bien_inmueble
        with self.assertRaises(ValidationError):
            Detalle720(
                tipo_registro=2,
                modelo="720",
                ejercicio=2024,
                nif_declarante="12345678Z",
                nif_declarado="12345678Z",
                nif_representante="",
                nombre_razon_declarado="Juan Perez Garcia",
                clave_condicion=1,
                tipo_titularidad_texto="",
                clave_tipo_bien=ClaveBien.B,
                subclave=1,
                tipo_derecho_real_inmueble="",
                codigo_pais="US",
                clave_identificacion=0,
                identificacion_valores="",
                clave_ident_cuenta="",
                codigo_bic="",
                codigo_cuenta="",
                identificacion_entidad="",  # Must be blank for B
                nif_entidad_pais_residencia="",  # Must be blank for B
                domicilio_via_num="Main St 123",
                domicilio_complemento="",
                domicilio_poblacion="New York",
                domicilio_region="NY",
                domicilio_cp="10001",
                domicilio_pais="US",
                fecha_incorporacion=date(2024, 1, 1),
                origen=Origen.A,
                fecha_extincion=None,
                valoracion_1=Valoracion(signo=" ", importe=Decimal("10000.00")),
                valoracion_2=Valoracion(signo=" ", importe=Decimal("0.00")),
                clave_repr_valores="",
                numero_valores_entera=0,
                numero_valores_decimal=0,
                clave_tipo_bien_inmueble="",  # Empty - should fail
                porcentaje_participacion_entera=100,
                porcentaje_participacion_decimal=0,
            )

    def test_detalle_max_length_constraints(self):
        """Test field length constraints."""
        detalle_data = self.create_valid_detalle().__dict__
        detalle_data["codigo_bic"] = "A" * 20  # Exceeds 11 chars
        with self.assertRaises(ValidationError):
            Detalle720(**detalle_data)


if __name__ == "__main__":
    unittest.main()
