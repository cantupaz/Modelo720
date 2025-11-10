"""This module provides data structures and validation logic for Modelo 720 declarations. """

from enum import Enum

from decimal import Decimal
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


MODEL_CODE = "720"

class DeclarationValidationError(Exception):
    """Raised when declaration validation fails."""
    pass


class ClaveBien(str, Enum):
    """Represents the type of asset in the Modelo 720 declaration."""
    C = "C"     # Cuentas bancarias o credito
    V = "V"     # Valores y derechos
    I = "I"     # Inmuebles
    S = "S"     # Seguros
    B = "B"     # Bienes muebles

class Origen(str, Enum):
    """Represents the origin of a detail record in the Modelo 720 declaration."""
    A = "A"     # Adquisición (bien que se declara por primera vez)
    M = "M"     # Modificación
    C = "C"     # Cancelación (se extingue la titularidad)  

@dataclass
class Valoracion:
    """Represents a valuation with a sign and an amount."""
    signo: str
    importe: Decimal
    

@dataclass
class Header720:
    """Represents a header record in the Modelo 720 declaration."""
    tipo_registro: int
    modelo: str
    ejercicio: int
    nif_declarante: str
    nombre_razon: str
    tipo_soporte: str
    telefono_contacto: Optional[str]
    persona_contacto: Optional[str]
    numero_identificativo: str
    declaracion_complementaria: bool
    declaracion_sustitutiva: bool
    numero_identificativo_anterior: Optional[str]
    numero_total_registros: int
    suma_valoracion_1: Valoracion
    suma_valoracion_2: Valoracion

@dataclass
class Detalle720:
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
    fecha_incorporacion: Optional[date]
    origen: Origen
    fecha_extincion: Optional[date]
    valoracion_1: Valoracion
    valoracion_2: Valoracion
    clave_repr_valores: str
    numero_valores_entera: int
    numero_valores_decimal: int
    clave_tipo_bien_inmueble: str
    porcentaje_participacion_entera: int
    porcentaje_participacion_decimal: int

@dataclass
class Declaration:
    """Represents a complete Modelo 720 declaration, including header and detail records."""
    header: Header720
    detalles: List[Detalle720] = field(default_factory=list)


    def print_detalle(self, detalle: Detalle720, idx: int):
        """Print a single detail record."""

        print(f"[{idx}] Bien {detalle.clave_tipo_bien.value} | País {detalle.codigo_pais} | Valor: {detalle.valoracion_1.importe}€")
        print(f"  Declarado: {detalle.nif_declarado} - {detalle.nombre_razon_declarado}")
        if detalle.fecha_incorporacion:
            print(f"  Fecha incorporación: {detalle.fecha_incorporacion}")
        if detalle.fecha_extincion:
            print(f"  Fecha extinción: {detalle.fecha_extincion}")
        print(f"  Porcentaje: {detalle.porcentaje_participacion_entera}.{detalle.porcentaje_participacion_decimal:02d}%")

    def print_declaration(self):
        """Print the entire declaration, including header and details."""
        
        print(f"Modelo {self.header.modelo} - Ejercicio {self.header.ejercicio}")
        print(f"Declarante: {self.header.nif_declarante} - {self.header.nombre_razon}")
        print(f"Número identificativo: {self.header.numero_identificativo}")
        print(f"Registros declarados: {self.header.numero_total_registros}")
        print(f"Suma valoración 1: {self.header.suma_valoracion_1.importe} | Suma valoración 2: {self.header.suma_valoracion_2.importe}")
        for i, d in enumerate(self.detalles, start=1):
            self.print_detalle(d, i)
    


    def validate(self) -> None:        
        """Validates the declaration form 720 by performing checks of header and detail records.
        
        Header Validation:
        - Ensures tipo_registro is set to 1 (required value)
        - Verifies modelo field matches MODEL_CODE (720)
        - Confirms numero_total_registros matches actual detail record count
        - Validates numero_identificativo is exactly 13 digits
        Detail Record Validation:
        - Ensures tipo_registro is set to 2 (required value)
        - For clave_tipo_bien 'I': ensures subclave is 0
        - For origen 'C': requires fecha_extincion to be specified
        - For clave_tipo_bien 'C': validates clave_ident_cuenta is 'I', 'O', or blank
        - For clave_tipo_bien 'B': validates clave_tipo_bien_inmueble is 'U', 'R', or blank
        Financial Validation:
        - Verifies suma_valoracion_1 in header equals sum of all detail valoracion_1 amounts
        - Verifies suma_valoracion_2 in header equals sum of all detail valoracion_2 amounts
        - Uses decimal precision comparison to avoid floating-point errors

        Raises:
            DeclarationValidationError: If any validation rule fails. The exception message
                                       contains all validation problems separated by semicolons.
        
        """

        problems = []
        h = self.header

        # Header validation
        if h.tipo_registro != 1:
            problems.append("Header tipo_registro must be 1")
        if h.modelo != MODEL_CODE:
            problems.append("Modelo must be 720")
        if h.numero_total_registros != len(self.detalles):
            problems.append(f"Número total de registros {h.numero_total_registros} does not match detail count {len(self.detalles)}")
        if not h.numero_identificativo.isdigit() or len(h.numero_identificativo) != 13:
            problems.append("Header numero_identificativo must be 13 digits")
        
        # Detail validation
        for i, d in enumerate(self.detalles, start=1):
            if d.tipo_registro != 2:
                problems.append(f"Detail {i}: tipo_registro must be 2")
            if d.clave_tipo_bien == ClaveBien.I and d.subclave != 0:
                problems.append(f"Detail {i}: subclave must be 0 for clave 'I'")
            if d.origen == Origen.C and d.fecha_extincion is None:
                problems.append(f"Detail {i}: origen 'C' requires fecha_extincion")
            if d.clave_tipo_bien == ClaveBien.C and d.clave_ident_cuenta not in ("I", "O", " "):
                problems.append(f"Detail {i}: clave_ident_cuenta must be I/O")
            if d.clave_tipo_bien == ClaveBien.B and d.clave_tipo_bien_inmueble not in ("U", "R", " "):
                problems.append(f"Detail {i}: tipo inmueble must be U/R")


        # Validate valoración sums
        sum1 = sum((d.valoracion_1.importe for d in self.detalles), Decimal("0"))
        if (sum1 - h.suma_valoracion_1.importe).copy_abs() > Decimal("0.00"):
            problems.append(f"SUMA VALORACIÓN 1 mismatch: header {h.suma_valoracion_1.importe} vs sum {sum1}")
        
        sum2 = sum((d.valoracion_2.importe for d in self.detalles), Decimal("0"))
        if (sum2 - h.suma_valoracion_2.importe).copy_abs() > Decimal("0.00"):
            problems.append(f"SUMA VALORACIÓN 2 mismatch: header {h.suma_valoracion_2.importe} vs sum {sum2}")


        if problems:
            raise DeclarationValidationError("; ".join(problems))

