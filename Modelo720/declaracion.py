"""This module provides data structures and validation logic for Modelo 720 declarations."""

from enum import Enum

from decimal import Decimal
from datetime import date
from typing import List, Optional, Literal

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

    tipo_registro: Literal[1] = Field(description="Tipo de registro (constante 1)")
    modelo: Literal["720"] = Field(
        max_length=3,
        description="Modelo declaración (constante 720)",
    )
    ejercicio: int = Field(description="Ejercicio fiscal")
    nif_declarante: str = Field(
        max_length=9,
        description="N.I.F. del declarante",
    )
    nombre_razon: str = Field(
        max_length=40,
        description="Apellidos y nombre o razón social del declarante",
    )
    tipo_soporte: Literal["T"] = Field(
        max_length=1,
        description="Tipo de soporte. Debe ser 'T': Transmisión Telemática",
    )
    telefono_contacto: Optional[str] = Field(
        default=None,
        max_length=9,
        description="Teléfono",
    )
    persona_contacto: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Apellidos y nombre de la persona con quien relacionarse",
    )
    numero_identificativo: str = Field(
        max_length=13, description="Número identificativo de la declaración"
    )
    declaracion_complementaria: bool = Field(description="Declaración complementaria")
    declaracion_sustitutiva: bool = Field(description="Declaración sustitutiva")
    numero_identificativo_anterior: Optional[str] = Field(
        default=None,
        max_length=13,
        description="Número identificativo de la declaración anterior",
    )
    numero_total_registros: int = Field(
        description="Número total de registros declarados"
    )
    suma_valoracion_1: Valoracion = Field(
        description="Suma total de valoración 1: Saldo o valor a 31 de diciembre; "
        "saldo o valor en la fecha de extinción; valor de adquisición"
    )
    suma_valoracion_2: Valoracion = Field(
        description="Suma total de valoración 2: Importe o valor de la transmisión; "
        "saldo medio último trimestre"
    )

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("nif_declarante")
    @classmethod
    def validate_nif_declarante(cls, v):
        """Validate NIF format for nif_declarante."""
        if not validar_nif(v):
            raise ValueError(f"Formato de NIF inválido para nif_declarante: {v}")
        return v.upper().strip()

    @field_validator("numero_identificativo")
    @classmethod
    def validate_numero_identificativo(cls, v):
        """Validate numero_identificativo format."""
        if not v.isdigit() or len(v) != 13:
            raise ValueError("El número identificativo debe tener 13 dígitos")
        if not v.startswith("720"):
            raise ValueError("El número identificativo debe comenzar con 720")
        return v

    @model_validator(mode="after")
    def validate_header_rules(self):
        """Validate business rules for header records."""
        # Ambas declaraciones no pueden ser verdaderas al mismo tiempo
        if self.declaracion_complementaria and self.declaracion_sustitutiva:
            raise ValueError(
                "No se puede marcar una declaración como complementaria "
                "y sustitutiva al mismo tiempo"
            )

        # Si es complementaria o sustitutiva, debe tener número anterior
        if self.declaracion_complementaria or self.declaracion_sustitutiva:
            if not self.numero_identificativo_anterior:
                raise ValueError(
                    "Se requiere numero_identificativo_anterior para declaraciones "
                    "complementarias o sustitutivas"
                )
            if (
                not self.numero_identificativo_anterior.isdigit()
                or len(self.numero_identificativo_anterior) != 13
            ):
                raise ValueError(
                    "El numero_identificativo_anterior debe tener 13 dígitos"
                )

        return self


class Detalle720(BaseModel):
    """Represents a detail record in the Modelo 720 declaration."""

    tipo_registro: Literal[2] = Field(
        description="Tipo de registro (constante 2 para registros de detalle)"
    )
    modelo: Literal["720"] = Field(
        max_length=3,
        description="Modelo de la declaración (constante 720)",
    )
    ejercicio: int = Field(description="Ejercicio fiscal")
    nif_declarante: str = Field(
        max_length=9,
        description="NIF del declarante",
    )
    nif_declarado: str = Field(
        max_length=9,
        description="NIF de la persona declarada",
    )
    nif_representante: str = Field(
        max_length=9,
        description="NIF del representante legal",
    )
    nombre_razon_declarado: str = Field(
        max_length=40,
        description="Nombre, razón social o denominación de la persona declarada",
    )
    clave_condicion: int = Field(
        ge=1,
        le=8,
        description="Código de condición del declarante (1-8)",
    )
    tipo_titularidad_texto: str = Field(
        max_length=25,
        description="Tipo de titularidad sobre el bien o derecho",
    )
    clave_tipo_bien: ClaveBien = Field(description="Clave de tipo de bien o derecho")
    subclave: int = Field(description="Subclave de bien o derecho")
    tipo_derecho_real_inmueble: str = Field(
        max_length=25,
        description="Tipo de derecho real sobre inmueble",
    )
    codigo_pais: str = Field(
        max_length=2,
        description="Código de país",
    )
    clave_identificacion: int = Field(description="Clave de identificación")
    identificacion_valores: str = Field(
        max_length=12,
        description="Identificación de valores",
    )
    clave_ident_cuenta: str = Field(
        max_length=1,
        description="Clave identificación de cuenta",
    )
    codigo_bic: str = Field(
        max_length=11,
        description="Código BIC",
    )
    codigo_cuenta: str = Field(
        max_length=34,
        description="Código de cuenta",
    )
    identificacion_entidad: str = Field(
        max_length=41,
        description="Identificación de la entidad",
    )
    nif_entidad_pais_residencia: str = Field(
        max_length=20,
        description="Número de identificación fiscal en el país de residencia fiscal",
    )
    domicilio_via_num: str = Field(
        max_length=52,
        description="Nombre vía pública y número de casa",
    )
    domicilio_complemento: str = Field(
        max_length=40,
        description="Complemento",
    )
    domicilio_poblacion: str = Field(
        max_length=30,
        description="Población/Ciudad",
    )
    domicilio_region: str = Field(
        max_length=30,
        description="Provincia/Región/Estado",
    )
    domicilio_cp: str = Field(
        max_length=10,
        description="Código postal (ZIP code)",
    )
    domicilio_pais: str = Field(
        max_length=2,
        description="Código país",
    )
    fecha_incorporacion: Optional[date] = Field(
        default=None, description="Fecha de incorporación"
    )
    origen: Origen = Field(description="Origen del bien o derecho")
    fecha_extincion: Optional[date] = Field(
        default=None, description="Fecha de extinción"
    )
    valoracion_1: Valoracion = Field(
        description="Valoración 1: Saldo o valor a 31 de diciembre; "
        "saldo o valor en la fecha de extinción; valor de adquisición"
    )
    valoracion_2: Valoracion = Field(
        description="Valoración 2: Importe o valor de la transmisión; "
        "saldo medio último trimestre"
    )
    clave_repr_valores: str = Field(
        max_length=1, description="Clave de representación de valores"
    )
    numero_valores_entera: int = Field(description="Número de valores (parte entera)")
    numero_valores_decimal: int = Field(description="Número de valores (parte decimal)")
    clave_tipo_bien_inmueble: str = Field(
        max_length=1, description="Clave tipo de bien inmueble"
    )
    porcentaje_participacion_entera: int = Field(
        description="Porcentaje de participación (parte entera)"
    )
    porcentaje_participacion_decimal: int = Field(
        description="Porcentaje de participación (parte decimal)"
    )

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("nif_declarante")
    @classmethod
    def validate_nif_declarante(cls, v):
        """Validate NIF format for nif_declarante."""
        if not validar_nif(v):
            raise ValueError(f"Invalid NIF format for nif_declarante: {v}")
        return v.upper().strip()

    @field_validator("nif_declarado")
    @classmethod
    def validate_nif_declarado(cls, v):
        """Validate NIF format for nif_declarado."""
        if v and not validar_nif(v):
            raise ValueError(f"Invalid NIF format for nif_declarado: {v}")
        return v.upper().strip() if v else v

    @field_validator("nif_representante")
    @classmethod
    def validate_nif_representante(cls, v):
        """Validate NIF format for nif_representante."""
        if v and not validar_nif(v):
            raise ValueError(f"Invalid NIF format for nif_representante: {v}")
        return v.upper().strip() if v else v

    @model_validator(mode="after")
    def validate_detail_rules(self):
        """Validate business rules for detail records."""
        # Subclave validation based on clave_tipo_bien
        if self.clave_tipo_bien == ClaveBien.I and self.subclave != 0:
            raise ValueError("subclave must be 0 for clave_tipo_bien 'I'")

        if self.clave_tipo_bien == ClaveBien.C and self.subclave not in (1, 2, 3, 4, 5):
            raise ValueError(
                "subclave debe ser 1-5 para clave_tipo_bien 'C' (bank accounts)"
            )

        if self.clave_tipo_bien == ClaveBien.V and self.subclave not in (1, 2, 3):
            raise ValueError(
                "subclave debe ser 1-3 para clave_tipo_bien 'V' (securities)"
            )

        if self.clave_tipo_bien == ClaveBien.S and self.subclave not in (1, 2):
            raise ValueError(
                "subclave debe ser 1-2 para clave_tipo_bien 'S' (insurance)"
            )
        if self.clave_tipo_bien == ClaveBien.B and self.subclave not in (1, 2, 3, 4, 5):
            raise ValueError(
                "subclave debe ser 1-5 para clave_tipo_bien 'B' (real estate)"
            )

        # tipo_derecho_real_inmueble only for B with subclave 5
        if self.clave_tipo_bien == ClaveBien.B and self.subclave == 5:
            if (
                not self.tipo_derecho_real_inmueble
                or not self.tipo_derecho_real_inmueble.strip()
            ):
                raise ValueError(
                    "tipo_derecho_real_inmueble es obligatorio cuando "
                    "clave_tipo_bien es 'B' y subclave es 5"
                )

        # Extinction date validation
        if self.origen == Origen.C and self.fecha_extincion is None:
            raise ValueError("origen 'C' requires fecha_extincion")

        # Account identification validation
        if self.clave_tipo_bien == ClaveBien.C and self.clave_ident_cuenta not in (
            "I",
            "O",
            " ",
            "",
        ):
            raise ValueError(
                "clave_ident_cuenta debe ser 'I', 'O', o en blanco para clave_tipo_bien 'C'"
            )

        # Real estate type validation
        if (
            self.clave_tipo_bien == ClaveBien.B
            and self.clave_tipo_bien_inmueble not in ("U", "R", " ", "")
        ):
            raise ValueError(
                "clave_tipo_bien_inmueble debe ser 'U', 'R', o en blanco para clave_tipo_bien 'B'"
            )

        # Real estate requires clave_tipo_bien_inmueble
        if self.clave_tipo_bien == ClaveBien.B:
            if (
                not self.clave_tipo_bien_inmueble
                or not self.clave_tipo_bien_inmueble.strip()
            ):
                raise ValueError(
                    "clave_tipo_bien_inmueble es obligatorio para clave_tipo_bien 'B'"
                )

        # clave_identificacion only for V or I
        if self.clave_tipo_bien in (ClaveBien.V, ClaveBien.I):
            if self.clave_identificacion not in (1, 2):
                raise ValueError(
                    "clave_identificacion debe ser 1 o 2 para clave_tipo_bien 'V' o 'I'"
                )
        else:
            if self.clave_identificacion != 0:
                raise ValueError(
                    "clave_identificacion debe ser 0 para clave_tipo_bien distinto de 'V' o 'I'"
                )

        # identificacion_valores only for V or I
        if self.clave_tipo_bien in (ClaveBien.V, ClaveBien.I):
            if (
                not self.identificacion_valores
                or not self.identificacion_valores.strip()
            ):
                raise ValueError(
                    "identificacion_valores es obligatorio para clave_tipo_bien 'V' o 'I'"
                )
        else:
            if self.identificacion_valores and self.identificacion_valores.strip():
                raise ValueError(
                    "identificacion_valores debe estar en blanco para "
                    "clave_tipo_bien distinto de 'V' o 'I'"
                )

        # clave_repr_valores and numero_valores only for V or I
        if self.clave_tipo_bien in (ClaveBien.V, ClaveBien.I):
            if not self.clave_repr_valores or self.clave_repr_valores not in ("A", "B"):
                raise ValueError(
                    "clave_repr_valores debe ser 'A' o 'B' para clave_tipo_bien 'V' o 'I'"
                )

        # identificacion_entidad must be blank for B
        if self.clave_tipo_bien == ClaveBien.B:
            if self.identificacion_entidad and self.identificacion_entidad.strip():
                raise ValueError(
                    "identificacion_entidad debe estar en blanco para clave_tipo_bien 'B'"
                )
            if (
                self.nif_entidad_pais_residencia
                and self.nif_entidad_pais_residencia.strip()
            ):
                raise ValueError(
                    "nif_entidad_pais_residencia debe estar en blanco para clave_tipo_bien 'B'"
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
            f"[{idx}] Bien {detalle.clave_tipo_bien.value} | "
            f"País {detalle.codigo_pais} | Valor: {detalle.valoracion_1.importe}€"
        )
        print(
            f"  Declarado: {detalle.nif_declarado} - {detalle.nombre_razon_declarado}"
        )
        if detalle.fecha_incorporacion:
            print(f"  Fecha incorporación: {detalle.fecha_incorporacion}")
        if detalle.fecha_extincion:
            print(f"  Fecha extinción: {detalle.fecha_extincion}")
        print(
            f"  Porcentaje: {detalle.porcentaje_participacion_entera}."
            f"{detalle.porcentaje_participacion_decimal:02d}%"
        )

    def print_declaration(self):
        """Print the entire declaration, including header and details."""

        print(f"Modelo {self.header.modelo} - Ejercicio {self.header.ejercicio}")
        print(f"Declarante: {self.header.nif_declarante} - {self.header.nombre_razon}")
        print(f"Número identificativo: {self.header.numero_identificativo}")
        print(f"Registros declarados: {self.header.numero_total_registros}")
        print(
            f"Suma valoración 1: {self.header.suma_valoracion_1.importe} "
            f"| Suma valoración 2: {self.header.suma_valoracion_2.importe}"
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
                f"Número total de registros {h.numero_total_registros} "
                f"no concuerda con el número de detalles {len(self.detalles)}"
            )

        # Validate valoración sums
        sum1 = sum((d.valoracion_1.importe for d in self.detalles), Decimal("0"))
        if (sum1 - h.suma_valoracion_1.importe).copy_abs() > Decimal("0.00"):
            problems.append(
                f"SUMA VALORACIÓN 1 no concuerda: encabezado {h.suma_valoracion_1.importe} "
                f"no concuerda con suma {sum1}"
            )

        sum2 = sum((d.valoracion_2.importe for d in self.detalles), Decimal("0"))
        if (sum2 - h.suma_valoracion_2.importe).copy_abs() > Decimal("0.00"):
            problems.append(
                f"SUMA VALORACIÓN 2 no concuerda: encabezado {h.suma_valoracion_2.importe} "
                f"no concuerda con suma {sum2}"
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
            raise DeclarationValidationError(str(e)) from e
