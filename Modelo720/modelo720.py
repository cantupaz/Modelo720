"""
Parser and validator for Agencia Tributaria Modelo 720 fixed‑width files.

Includes reading, validation, structured storage, and pretty printing of data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from typing import Iterable, List, Optional, Union
import re

LINE_LEN = 500
MODEL_CODE = "720"

def _slice(line: str, start: int, end: int) -> str:
    return line[start - 1 : end]

def _to_int(s: str) -> int:
    s = s.strip()
    if not s:
        return 0
    if not re.fullmatch(r"[0-9]+", s):
        raise ValueError(f"Expected numeric, got {s!r}")
    return int(s)

def _to_decimal_from_cents(sign_char: str, cents_str: str) -> Decimal:
    if not cents_str.strip():
        return Decimal("0.00")
    if not re.fullmatch(r"[0-9]+", cents_str):
        raise ValueError(f"Expected numeric cents, got {cents_str!r}")
    val = Decimal(int(cents_str)).scaleb(-2)
    if sign_char == "N":
        val = -val
    return val.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def _to_date8(s: str) -> Optional[date]:
    s = s.strip()
    if not s:
        return None
    if not re.fullmatch(r"[0-9]{8}", s):
        raise ValueError(f"Expected AAAAMMDD, got {s!r}")
    y, m, d = int(s[:4]), int(s[4:6]), int(s[6:8])
    return date(y, m, d)

def _only_upper_ia5(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9 ÑÇ&./'()-]*", s))

class ClaveBien(str, Enum):
    C = "C"
    V = "V"
    I = "I"
    S = "S"
    B = "B"

class Origen(str, Enum):
    A = "A"
    M = "M"
    C = "C"

@dataclass
class Valoracion:
    signo: str
    importe: Decimal

@dataclass
class Header720:
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
    header: Header720
    detalles: List[Detalle720] = field(default_factory=list)

class Modelo720FormatError(Exception):
    pass

def _parse_header(line: str) -> Header720:
    tipo_registro = _to_int(_slice(line, 1, 1))
    modelo = _slice(line, 2, 4)
    ejercicio = _to_int(_slice(line, 5, 8))
    nif_declarante = _slice(line, 9, 17)
    nombre_razon = _slice(line, 18, 57).rstrip()
    tipo_soporte = _slice(line, 58, 58)
    telefono_contacto = _slice(line, 59, 67).strip() or None
    persona_contacto = _slice(line, 68, 107).rstrip() or None
    numero_identificativo = _slice(line, 108, 120)
    declaracion_complementaria = _slice(line, 121, 121) == "C"
    declaracion_sustitutiva = _slice(line, 122, 122) == "S"
    numero_identificativo_anterior = _slice(line, 123, 135).strip() or None
    numero_total_registros = _to_int(_slice(line, 136, 144))
    signo1 = _slice(line, 145, 145)
    imp1 = _slice(line, 146, 162)
    suma_valoracion_1 = Valoracion(signo1, _to_decimal_from_cents(signo1, imp1))
    signo2 = _slice(line, 163, 163)
    imp2 = _slice(line, 164, 180)
    suma_valoracion_2 = Valoracion(signo2, _to_decimal_from_cents(signo2, imp2))
    return Header720(tipo_registro, modelo, ejercicio, nif_declarante, nombre_razon,
                     tipo_soporte, telefono_contacto, persona_contacto,
                     numero_identificativo, declaracion_complementaria,
                     declaracion_sustitutiva, numero_identificativo_anterior,
                     numero_total_registros, suma_valoracion_1, suma_valoracion_2)

def _parse_detalle(line: str) -> Detalle720:
    tipo_registro = _to_int(_slice(line, 1, 1))
    modelo = _slice(line, 2, 4)
    ejercicio = _to_int(_slice(line, 5, 8))
    nif_declarante = _slice(line, 9, 17)
    nif_declarado = _slice(line, 18, 26)
    nif_repr = _slice(line, 27, 35)
    nombre_razon_declarado = _slice(line, 36, 75).rstrip()
    clave_condicion = _to_int(_slice(line, 76, 76))
    tipo_titularidad_texto = _slice(line, 77, 101).rstrip()
    clave_tipo_bien = ClaveBien(_slice(line, 102, 102))
    subclave = _to_int(_slice(line, 103, 103))
    tipo_dcho_real_inm = _slice(line, 104, 128).rstrip()
    codigo_pais = _slice(line, 129, 130)
    clave_identificacion = _to_int(_slice(line, 131, 131))
    ident_valores = _slice(line, 132, 143).rstrip()
    clave_ident_cuenta = _slice(line, 144, 144)
    codigo_bic = _slice(line, 145, 155).rstrip()
    codigo_cuenta = _slice(line, 156, 189).rstrip()
    identificacion_entidad = _slice(line, 190, 230).rstrip()
    nif_entidad_pais_res = _slice(line, 231, 250).rstrip()
    dom_via = _slice(line, 251, 302).rstrip()
    dom_compl = _slice(line, 303, 342).rstrip()
    dom_pobl = _slice(line, 343, 372).rstrip()
    dom_region = _slice(line, 373, 402).rstrip()
    dom_cp = _slice(line, 403, 412).rstrip()
    dom_pais = _slice(line, 413, 414)
    fecha_incorp = _to_date8(_slice(line, 415, 422))
    origen = Origen(_slice(line, 423, 423))
    fecha_ext = _to_date8(_slice(line, 424, 431))
    signo1 = _slice(line, 432, 432)
    imp1 = _slice(line, 433, 446)
    valor1 = Valoracion(signo1, _to_decimal_from_cents(signo1, imp1))
    signo2 = _slice(line, 447, 447)
    imp2 = _slice(line, 448, 461)
    valor2 = Valoracion(signo2, _to_decimal_from_cents(signo2, imp2))
    clave_repr_vals = _slice(line, 462, 462)
    num_vals_ent = _to_int(_slice(line, 463, 472))
    num_vals_dec = _to_int(_slice(line, 473, 474))
    clave_tipo_bien_inm = _slice(line, 475, 475)
    part_ent = _to_int(_slice(line, 476, 478))
    part_dec = _to_int(_slice(line, 479, 480))
    return Detalle720(tipo_registro, modelo, ejercicio, nif_declarante, nif_declarado,
                      nif_repr, nombre_razon_declarado, clave_condicion,
                      tipo_titularidad_texto, clave_tipo_bien, subclave,
                      tipo_dcho_real_inm, codigo_pais, clave_identificacion,
                      ident_valores, clave_ident_cuenta, codigo_bic, codigo_cuenta,
                      identificacion_entidad, nif_entidad_pais_res, dom_via,
                      dom_compl, dom_pobl, dom_region, dom_cp, dom_pais,
                      fecha_incorp, origen, fecha_ext, valor1, valor2,
                      clave_repr_vals, num_vals_ent, num_vals_dec,
                      clave_tipo_bien_inm, part_ent, part_dec)

def _iter_lines(path_or_stream: Union[str, Iterable[str]]) -> Iterable[str]:
    if isinstance(path_or_stream, str):
        with open(path_or_stream, "r", encoding="latin-1") as f:
            for ln in f:
                yield ln.rstrip("\n\r")
    else:
        for ln in path_or_stream:
            yield ln.rstrip("\n\r")

def read_modelo720(path_or_stream: Union[str, Iterable[str]]) -> Declaration:
    lines = [ln for ln in _iter_lines(path_or_stream) if ln.strip()]
    header = _parse_header(lines[0])
    detalles = [_parse_detalle(ln) for ln in lines[1:]]
    return Declaration(header, detalles)

def validate(declaration: Declaration) -> List[str]:
    problems: List[str] = []
    h = declaration.header
    if h.tipo_registro != 1:
        problems.append("Header tipo_registro must be 1")
    if h.modelo != MODEL_CODE:
        problems.append("Modelo must be 720")
    if h.numero_total_registros != len(declaration.detalles):
        problems.append("Número total de registros does not match detail count")
    sum1 = sum((d.valoracion_1.importe for d in declaration.detalles), Decimal("0"))
    if (sum1 - h.suma_valoracion_1.importe).copy_abs() > Decimal("0.00"):
        problems.append("SUMA VALORACIÓN 1 mismatch")
    return problems

def to_dict(declaration: Declaration) -> dict:
    return {
        "header": declaration.header.__dict__,
        "detalles": [d.__dict__ for d in declaration.detalles],
    }

# ----------------- Printing functions ------------------

def print_header(header: Header720):
    print(f"Modelo {header.modelo} - Ejercicio {header.ejercicio}")
    print(f"Declarante: {header.nif_declarante} - {header.nombre_razon}")
    print(f"Número identificativo: {header.numero_identificativo}")
    print(f"Registros declarados: {header.numero_total_registros}")
    print(f"Suma valoración 1: {header.suma_valoracion_1.importe} | Suma valoración 2: {header.suma_valoracion_2.importe}")

def print_detalle(detalle: Detalle720, idx: int):
    print(f"[{idx}] Bien {detalle.clave_tipo_bien.value} | País {detalle.codigo_pais} | Valor: {detalle.valoracion_1.importe}€")
    print(f"  Declarado: {detalle.nif_declarado} - {detalle.nombre_razon_declarado}")
    if detalle.fecha_incorporacion:
        print(f"  Fecha incorporación: {detalle.fecha_incorporacion}")
    if detalle.fecha_extincion:
        print(f"  Fecha extinción: {detalle.fecha_extincion}")
    print(f"  Porcentaje: {detalle.porcentaje_participacion_entera}.{detalle.porcentaje_participacion_decimal:02d}%")

def print_declaration(declaration: Declaration):
    print_header(declaration.header)
    for i, d in enumerate(declaration.detalles, start=1):
        print_detalle(d, i)

__all__ = ["Modelo720FormatError", "Header720", "Detalle720", "Declaration", "read_modelo720", "validate", "to_dict", "print_header", "print_detalle", "print_declaration"]
