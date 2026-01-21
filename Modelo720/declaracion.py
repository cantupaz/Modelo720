"""This module provides data structures and validation logic for Modelo 720 declarations."""

from enum import Enum

from decimal import Decimal
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


MODEL_CODE = "720"


def validar_nif(nif: str) -> bool:
    """Valida un DNI español (8 números + 1 letra) o NIE (1 letra + 7 números + 1 letra)."""
    if not nif:
        return False
    nif = nif.upper().strip()
    if len(nif) == 9 and nif[:8].isdigit():
        # Caso DNI estándar
        numero = int(nif[:8])
        letra_control = nif[8]
        tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
        return tabla[numero % 23] == letra_control
    elif len(nif) == 9 and nif[0] in "XYZ" and nif[1:8].isdigit():
        # Caso NIE
        reemplazo = {"X": "0", "Y": "1", "Z": "2"}
        num_nie = reemplazo[nif[0]] + nif[1:8]
        letra_control = nif[8]
        tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
        return tabla[int(num_nie) % 23] == letra_control
    else:
        return False


class DeclarationValidationError(Exception):
    """Raised when declaration validation fails."""

    pass


class ClaveBien(str, Enum):
    """Represents the type of asset in the Modelo 720 declaration."""

    C = "C"  # Cuentas bancarias o credito
    V = "V"  # Valores y derechos
    I = "I"  # Inmuebles
    S = "S"  # Seguros
    B = "B"  # Bienes muebles


class Origen(str, Enum):
    """Represents the origin of a detail record in the Modelo 720 declaration."""

    A = "A"  # Adquisición (bien que se declara por primera vez)
    M = "M"  # Modificación
    C = "C"  # Cancelación (se extingue la titularidad)


class Valoracion(BaseModel):
    """Represents a valuation with a sign and an amount."""

    signo: str
    importe: Decimal

    model_config = {"arbitrary_types_allowed": True}


class Header720(BaseModel):
    """Represents a header record in the Modelo 720 declaration."""

    tipo_registro: int
    modelo: str
    ejercicio: int
    nif_declarante: str
    nombre_razon: str
    tipo_soporte: str
    telefono_contacto: Optional[str] = None
    persona_contacto: Optional[str] = None
    numero_identificativo: str
    declaracion_complementaria: bool
    declaracion_sustitutiva: bool
    numero_identificativo_anterior: Optional[str] = None
    numero_total_registros: int
    suma_valoracion_1: Valoracion
    suma_valoracion_2: Valoracion

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("tipo_registro")
    @classmethod
    def validate_tipo_registro(cls, v):
        if v != 1:
            raise ValueError("Header tipo_registro must be 1")
        return v

    @field_validator("nif_declarante")
    @classmethod
    def validate_nif_declarante(cls, v):
        if not validar_nif(v):
            raise ValueError(f"Invalid NIF format for nif_declarante: {v}")
        return v.upper().strip()

    @field_validator("modelo")
    @classmethod
    def validate_modelo(cls, v):
        if v != MODEL_CODE:
            raise ValueError(f"Modelo must be {MODEL_CODE}")
        return v

    @field_validator("numero_identificativo")
    @classmethod
    def validate_numero_identificativo(cls, v):
        if not v.isdigit() or len(v) != 13:
            raise ValueError("Header numero_identificativo must be 13 digits")
        return v


class Detalle720(BaseModel):
    """Represents a detail record in the Modelo 720 declaration."""

    tipo_registro: int
    modelo: str
    ejercicio: int
    nif_declarante: str
    nif_declarado: str
    nif_representante: str
    nombre_razon_declarado: str
    clave_condicion: int
    tipo_titularidad_texto: str
    clave_tipo_bien: ClaveBien
    subclave: int
    tipo_derecho_real_inmueble: str
    codigo_pais: str
    clave_identificacion: int
    identificacion_valores: str
    clave_ident_cuenta: str
    codigo_bic: str
    codigo_cuenta: str
    identificacion_entidad: str
    nif_entidad_pais_residencia: str
    domicilio_via_num: str
    domicilio_complemento: str
    domicilio_poblacion: str
    domicilio_region: str
    domicilio_cp: str
    domicilio_pais: str
    fecha_incorporacion: Optional[date] = None
    origen: Origen
    fecha_extincion: Optional[date] = None
    valoracion_1: Valoracion
    valoracion_2: Valoracion
    clave_repr_valores: str
    numero_valores_entera: int
    numero_valores_decimal: int
    clave_tipo_bien_inmueble: str
    porcentaje_participacion_entera: int
    porcentaje_participacion_decimal: int

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("tipo_registro")
    @classmethod
    def validate_tipo_registro(cls, v):
        if v != 2:
            raise ValueError("Detail tipo_registro must be 2")
        return v

    @field_validator("nif_declarante")
    @classmethod
    def validate_nif_declarante(cls, v):
        if not validar_nif(v):
            raise ValueError(f"Invalid NIF format for nif_declarante: {v}")
        return v.upper().strip()

    @field_validator("nif_declarado")
    @classmethod
    def validate_nif_declarado(cls, v):
        if v and not validar_nif(v):
            raise ValueError(f"Invalid NIF format for nif_declarado: {v}")
        return v.upper().strip() if v else v

    @field_validator("nif_representante")
    @classmethod
    def validate_nif_representante(cls, v):
        if v and not validar_nif(v):
            raise ValueError(f"Invalid NIF format for nif_representante: {v}")
        return v.upper().strip() if v else v

    @model_validator(mode="after")
    def validate_detail_rules(self):
        """Validate business rules for detail records."""
        if self.clave_tipo_bien == ClaveBien.I and self.subclave != 0:
            raise ValueError("subclave must be 0 for clave_tipo_bien 'I'")

        if self.origen == Origen.C and self.fecha_extincion is None:
            raise ValueError("origen 'C' requires fecha_extincion")

        if self.clave_tipo_bien == ClaveBien.C and self.clave_ident_cuenta not in (
            "I",
            "O",
            " ",
            "",
        ):
            raise ValueError(
                "clave_ident_cuenta must be 'I', 'O', or blank for clave_tipo_bien 'C'"
            )

        if (
            self.clave_tipo_bien == ClaveBien.B
            and self.clave_tipo_bien_inmueble not in ("U", "R", " ", "")
        ):
            raise ValueError(
                "clave_tipo_bien_inmueble must be 'U', 'R', or blank for clave_tipo_bien 'B'"
            )

        return self


class Declaration(BaseModel):
    """Represents a complete Modelo 720 declaration, including header and detail records."""

    header: Header720
    detalles: List[Detalle720] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}

    def print_detalle(self, detalle: Detalle720, idx: int):
        """Print a single detail record."""

        print(
            f"[{idx}] Bien {detalle.clave_tipo_bien.value} | País {detalle.codigo_pais} | Valor: {detalle.valoracion_1.importe}€"
        )
        print(
            f"  Declarado: {detalle.nif_declarado} - {detalle.nombre_razon_declarado}"
        )
        if detalle.fecha_incorporacion:
            print(f"  Fecha incorporación: {detalle.fecha_incorporacion}")
        if detalle.fecha_extincion:
            print(f"  Fecha extinción: {detalle.fecha_extincion}")
        print(
            f"  Porcentaje: {detalle.porcentaje_participacion_entera}.{detalle.porcentaje_participacion_decimal:02d}%"
        )

    def print_declaration(self):
        """Print the entire declaration, including header and details."""

        print(f"Modelo {self.header.modelo} - Ejercicio {self.header.ejercicio}")
        print(f"Declarante: {self.header.nif_declarante} - {self.header.nombre_razon}")
        print(f"Número identificativo: {self.header.numero_identificativo}")
        print(f"Registros declarados: {self.header.numero_total_registros}")
        print(
            f"Suma valoración 1: {self.header.suma_valoracion_1.importe} | Suma valoración 2: {self.header.suma_valoracion_2.importe}"
        )
        for i, d in enumerate(self.detalles, start=1):
            self.print_detalle(d, i)

    @model_validator(mode="after")
    def validate_business_rules(self):
        """Validates business logic like record counts and sum totals.

        This method validates:
        - numero_total_registros matches actual detail record count
        - suma_valoracion_1 in header equals sum of all detail valoracion_1 amounts
        - suma_valoracion_2 in header equals sum of all detail valoracion_2 amounts

        Note: Input validation (field types, required fields, etc.) is handled
        automatically by Pydantic validators on individual fields.
        """
        problems = []
        h = self.header

        # Validate record count
        if h.numero_total_registros != len(self.detalles):
            problems.append(
                f"Número total de registros {h.numero_total_registros} does not match detail count {len(self.detalles)}"
            )

        # Validate valoración sums
        sum1 = sum((d.valoracion_1.importe for d in self.detalles), Decimal("0"))
        if (sum1 - h.suma_valoracion_1.importe).copy_abs() > Decimal("0.00"):
            problems.append(
                f"SUMA VALORACIÓN 1 mismatch: header {h.suma_valoracion_1.importe} vs sum {sum1}"
            )

        sum2 = sum((d.valoracion_2.importe for d in self.detalles), Decimal("0"))
        if (sum2 - h.suma_valoracion_2.importe).copy_abs() > Decimal("0.00"):
            problems.append(
                f"SUMA VALORACIÓN 2 mismatch: header {h.suma_valoracion_2.importe} vs sum {sum2}"
            )

        if problems:
            raise ValueError("; ".join(problems))

        return self

    def validate(self) -> None:
        """Legacy validate method for backward compatibility.

        Note: Most validation is now handled automatically by Pydantic.
        This method is kept for explicit validation calls and will raise
        DeclarationValidationError to maintain API compatibility.

        Raises:
            DeclarationValidationError: If any validation rule fails.
        """
        try:
            # Trigger Pydantic validation by accessing model_validate
            self.model_validate(self.model_dump())
        except ValueError as e:
            raise DeclarationValidationError(str(e))
