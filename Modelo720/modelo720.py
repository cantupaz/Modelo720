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
    if not s or s=="00000000":
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

# ================= CSV I/O (two-section CSV) =================
import csv
from typing import TextIO

HEADER_FIELDS_ORDER = [
    "tipo_registro","modelo","ejercicio","nif_declarante","nombre_razon",
    "tipo_soporte","telefono_contacto","persona_contacto","numero_identificativo",
    "declaracion_complementaria","declaracion_sustitutiva","numero_identificativo_anterior",
    "numero_total_registros","suma_valoracion_1","suma_valoracion_2"
]

DETALLE_FIELDS_ORDER = [
    "tipo_registro","modelo","ejercicio","nif_declarante","nif_declarado","nif_representante",
    "nombre_razon_declarado","clave_condicion","tipo_titularidad_texto","clave_tipo_bien","subclave",
    "tipo_derecho_real_inmueble","codigo_pais","clave_identificacion","identificacion_valores",
    "clave_ident_cuenta","codigo_bic","codigo_cuenta","identificacion_entidad","nif_entidad_pais_residencia",
    "domicilio_via_num","domicilio_complemento","domicilio_poblacion","domicilio_region","domicilio_cp",
    "domicilio_pais","fecha_incorporacion","origen","fecha_extincion","valoracion_1","valoracion_2",
    "clave_repr_valores","numero_valores_entera","numero_valores_decimal","clave_tipo_bien_inmueble",
    "porcentaje_participacion_entera","porcentaje_participacion_decimal"
]

_LEN = {
    "nif_declarante": 9,
    "nombre_razon": 40,
    "tipo_soporte": 1,
    "telefono_contacto": 9,
    "persona_contacto": 40,
    "numero_identificativo": 13,
    "nif_declarado": 9,
    "nif_representante": 9,
    "nombre_razon_declarado": 40,
    "tipo_titularidad_texto": 25,
    "subclave": 1,
    "tipo_derecho_real_inmueble": 25,
    "codigo_pais": 2,
    "identificacion_valores": 12,
    "clave_ident_cuenta": 1,
    "codigo_bic": 11,
    "codigo_cuenta": 34,
    "identificacion_entidad": 41,
    "nif_entidad_pais_residencia": 20,
    "domicilio_via_num": 52,
    "domicilio_complemento": 40,
    "domicilio_poblacion": 30,
    "domicilio_region": 30,
    "domicilio_cp": 10,
    "domicilio_pais": 2,
}

class CSV720Error(Exception):
    pass

_DEF_HEADER_DEFAULTS = {"tipo_registro": 1, "modelo": MODEL_CODE}

def _bool_to_str(b: bool) -> str:
    return "1" if b else "0"

def _str_to_bool(s: str) -> bool:
    s = (s or "").strip().lower()
    return s in {"1","true","t","yes","y","si","sí"}


def write_csv(declaration: Declaration, fp: Union[str, TextIO]):
    """Write a single CSV file with two sections: HEADER and DETALLES."""
    need_close = False
    if isinstance(fp, str):
        f = open(fp, "w", newline="", encoding="utf-8")
        need_close = True
    else:
        f = fp
    try:
        w = csv.writer(f)
        # Header section
        w.writerow(["__SECTION__","HEADER"])
        w.writerow(["field","value"])  # informational header row
        h = declaration.header
        def _hv(name: str) -> str:
            if name == "suma_valoracion_1":
                return str(h.suma_valoracion_1.importe)
            if name == "suma_valoracion_2":
                return str(h.suma_valoracion_2.importe)
            v = getattr(h, name)
            if isinstance(v, bool):
                return _bool_to_str(v)
            return "" if v is None else str(v)
        for name in HEADER_FIELDS_ORDER:
            w.writerow([name, _hv(name)])
        # Details section
        w.writerow(["__SECTION__","DETALLES"])
        w.writerow(DETALLE_FIELDS_ORDER)
        for d in declaration.detalles:
            def _dv(name: str):
                v = getattr(d, name)
                if isinstance(v, Enum):
                    return v.value
                if isinstance(v, date):
                    return v.isoformat()
                if isinstance(v, Valoracion):
                    return str(v.importe)
                return "" if v is None else str(v)
            w.writerow([_dv(n) for n in DETALLE_FIELDS_ORDER])
    finally:
        if need_close:
            f.close()


def _parse_decimal_euros(s: str) -> Valoracion:
    s = (s or "").strip()
    if not s:
        return Valoracion(" ", Decimal("0.00"))
    d = Decimal(s)
    signo = "N" if d < 0 else " "
    return Valoracion(signo, abs(d).quantize(Decimal("0.01"), rounding=ROUND_DOWN))


def read_csv(fp: Union[str, TextIO]) -> Declaration:
    """Read a two-section CSV (HEADER then DETALLES) and return a Declaration.
    Performs type/length/enum checks similar to the fixed-width spec.
    """
    need_close = False
    if isinstance(fp, str):
        f = open(fp, "r", newline="", encoding="utf-8")
        need_close = True
    else:
        f = fp
    try:
        r = csv.reader(f)
        rows = list(r)
    finally:
        if need_close:
            f.close()

    try:
        header_start = next(i for i,row in enumerate(rows) if row[:2]==["__SECTION__","HEADER"]) + 1
        detalles_start = next(i for i,row in enumerate(rows) if row[:2]==["__SECTION__","DETALLES"]) + 1
    except StopIteration:
        raise CSV720Error("Missing __SECTION__ markers for HEADER/DETALLES")

    header_table = rows[header_start:detalles_start-1]
    if not header_table:
        raise CSV720Error("Empty header section")
    if header_table and header_table[0][:2] == ["field","value"]:
        header_table = header_table[1:]
    hvals = {k: v for k,v,*_ in header_table}
    for k,v in _DEF_HEADER_DEFAULTS.items():
        hvals.setdefault(k, v)

    try:
        ejercicio = int(hvals.get("ejercicio"))
    except Exception:
        raise CSV720Error("Header 'ejercicio' must be integer")
    numero_total_registros = int(hvals.get("numero_total_registros", 0) or 0)
    suma_val1 = _parse_decimal_euros(hvals.get("suma_valoracion_1","0"))
    suma_val2 = _parse_decimal_euros(hvals.get("suma_valoracion_2","0"))

    header = Header720(
        tipo_registro=int(hvals.get("tipo_registro",1)),
        modelo=hvals.get("modelo", MODEL_CODE),
        ejercicio=ejercicio,
        nif_declarante=(hvals.get("nif_declarante") or ""),
        nombre_razon=(hvals.get("nombre_razon") or ""),
        tipo_soporte=(hvals.get("tipo_soporte") or " "),
        telefono_contacto=hvals.get("telefono_contacto") or None,
        persona_contacto=hvals.get("persona_contacto") or None,
        numero_identificativo=(hvals.get("numero_identificativo") or ""),
        declaracion_complementaria=_str_to_bool(hvals.get("declaracion_complementaria")),
        declaracion_sustitutiva=_str_to_bool(hvals.get("declaracion_sustitutiva")),
        numero_identificativo_anterior=hvals.get("numero_identificativo_anterior") or None,
        numero_total_registros=numero_total_registros,
        suma_valoracion_1=suma_val1,
        suma_valoracion_2=suma_val2,
    )

    det_header = rows[detalles_start]
    if det_header != DETALLE_FIELDS_ORDER:
        raise CSV720Error("Detalles header row does not match expected columns")
    det_rows = rows[detalles_start+1:]

    detalles: List[Detalle720] = []
    for ridx, row in enumerate(det_rows, start=1):
        if not any((c or '').strip() for c in row):
            continue
        vals = dict(zip(DETALLE_FIELDS_ORDER, row))
        def _req_int(name: str) -> int:
            try:
                return int((vals.get(name) or "0").strip() or 0)
            except Exception:
                raise CSV720Error(f"Detail row {ridx}: field '{name}' must be integer")
        def _opt_date(name: str):
            s = (vals.get(name) or "").strip()
            if not s:
                return None
            try:
                return date.fromisoformat(s)
            except Exception:
                raise CSV720Error(f"Detail row {ridx}: field '{name}' must be YYYY-MM-DD")
        def _str_max(name: str) -> str:
            s = (vals.get(name) or "").strip()
            maxlen = _LEN.get(name)
            if maxlen is not None and len(s) > maxlen:
                raise CSV720Error(f"Detail row {ridx}: field '{name}' exceeds max length {maxlen}")
            return s
        def _enum(enum_cls, name: str):
            s = (vals.get(name) or "").strip()
            if not s:
                raise CSV720Error(f"Detail row {ridx}: field '{name}' is required")
            try:
                return enum_cls(s)
            except Exception:
                raise CSV720Error(f"Detail row {ridx}: field '{name}' invalid value '{s}'")
        def _valor(name: str) -> Valoracion:
            return _parse_decimal_euros(vals.get(name))

        d = Detalle720(
            tipo_registro=_req_int("tipo_registro"),
            modelo=_str_max("modelo"),
            ejercicio=_req_int("ejercicio"),
            nif_declarante=_str_max("nif_declarante"),
            nif_declarado=_str_max("nif_declarado"),
            nif_representante=_str_max("nif_representante"),
            nombre_razon_declarado=_str_max("nombre_razon_declarado"),
            clave_condicion=_req_int("clave_condicion"),
            tipo_titularidad_texto=_str_max("tipo_titularidad_texto"),
            clave_tipo_bien=_enum(ClaveBien, "clave_tipo_bien"),
            subclave=_req_int("subclave"),
            tipo_derecho_real_inmueble=_str_max("tipo_derecho_real_inmueble"),
            codigo_pais=_str_max("codigo_pais"),
            clave_identificacion=_req_int("clave_identificacion"),
            identificacion_valores=_str_max("identificacion_valores"),
            clave_ident_cuenta=_str_max("clave_ident_cuenta"),
            codigo_bic=_str_max("codigo_bic"),
            codigo_cuenta=_str_max("codigo_cuenta"),
            identificacion_entidad=_str_max("identificacion_entidad"),
            nif_entidad_pais_residencia=_str_max("nif_entidad_pais_residencia"),
            domicilio_via_num=_str_max("domicilio_via_num"),
            domicilio_complemento=_str_max("domicilio_complemento"),
            domicilio_poblacion=_str_max("domicilio_poblacion"),
            domicilio_region=_str_max("domicilio_region"),
            domicilio_cp=_str_max("domicilio_cp"),
            domicilio_pais=_str_max("domicilio_pais"),
            fecha_incorporacion=_opt_date("fecha_incorporacion"),
            origen=_enum(Origen, "origen"),
            fecha_extincion=_opt_date("fecha_extincion"),
            valoracion_1=_valor("valoracion_1"),
            valoracion_2=_valor("valoracion_2"),
            clave_repr_valores=_str_max("clave_repr_valores"),
            numero_valores_entera=_req_int("numero_valores_entera"),
            numero_valores_decimal=_req_int("numero_valores_decimal"),
            clave_tipo_bien_inmueble=_str_max("clave_tipo_bien_inmueble"),
            porcentaje_participacion_entera=_req_int("porcentaje_participacion_entera"),
            porcentaje_participacion_decimal=_req_int("porcentaje_participacion_decimal"),
        )
        detalles.append(d)

    dec = Declaration(header, detalles)

    # Extra logical checks
    strict = []
    if header.modelo != MODEL_CODE:
        strict.append("Header modelo must be '720'")
    if not header.numero_identificativo.isdigit() or len(header.numero_identificativo) != 13:
        strict.append("Header numero_identificativo must be 13 digits")
    if len(header.nombre_razon) > _LEN["nombre_razon"]:
        strict.append("Header nombre_razon too long")
    for i,d in enumerate(detalles, start=1):
        if d.clave_tipo_bien == ClaveBien.I and d.subclave != 0:
            strict.append(f"Detail {i}: subclave must be 0 for clave 'I'")
        if d.origen == Origen.C and d.fecha_extincion is None:
            strict.append(f"Detail {i}: origen 'C' requires fecha_extincion")
        if d.clave_tipo_bien == ClaveBien.C and d.clave_ident_cuenta not in ("I","O"," "):
            strict.append(f"Detail {i}: clave_ident_cuenta must be I/O")
        if d.clave_tipo_bien == ClaveBien.B and d.clave_tipo_bien_inmueble not in ("U","R"," "):
            strict.append(f"Detail {i}: tipo inmueble must be U/R")
    if strict:
        raise CSV720Error("; ".join(strict))

    return dec

# Override exported names to include CSV helpers
__all__ = [
    "Modelo720FormatError","Header720","Detalle720","Declaration",
    "read_modelo720","validate","to_dict","print_header","print_detalle",
    "print_declaration","write_csv","read_csv","CSV720Error"
]

