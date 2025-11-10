"""
Parser and Writer for Agencia Tributaria Modelo 720 fixed-width and proprietary CSV files.

The fixed-width format is the official format used by the Agencia Tributaria for Modelo 720 declarations.

The proprietary CSV format is an alternative format that is intended as an easy way to enter and read data. 
The CSV format preserves all data fields and structure.

"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from typing import Iterable, List, Optional, Union, TextIO
import re

from .declaracion import Declaration, MODEL_CODE, ClaveBien, Origen, Valoracion, Header720, Detalle720, DeclarationValidationError

@dataclass
class FieldSpec:
    """Specification for a field in the Modelo 720 format."""
    name: str
    start: int          # 1-based position in fixed-width line
    end: int            # 1-based position in fixed-width line
    transform: str      # Transform type: "int", "str", "date8", "decimal_cents", "bool_c", "bool_s", "enum"
    enum_class: Optional[type] = None  # For enum transforms
    required: bool = True
    csv_include: bool = True


# Field specifications preserving exact current order and positions
HEADER_FIELDS = [
    FieldSpec("tipo_registro", 1, 1, "int"),
    FieldSpec("modelo", 2, 4, "str"),
    FieldSpec("ejercicio", 5, 8, "int"),
    FieldSpec("nif_declarante", 9, 17, "str"),
    FieldSpec("nombre_razon", 18, 57, "str"),
    FieldSpec("tipo_soporte", 58, 58, "str"),
    FieldSpec("telefono_contacto", 59, 67, "str", required=False),
    FieldSpec("persona_contacto", 68, 107, "str", required=False),
    FieldSpec("numero_identificativo", 108, 120, "str"),
    FieldSpec("declaracion_complementaria", 121, 121, "bool_c"),
    FieldSpec("declaracion_sustitutiva", 122, 122, "bool_s"),
    FieldSpec("numero_identificativo_anterior", 123, 135, "str", required=False),
    FieldSpec("numero_total_registros", 136, 144, "int"),
    FieldSpec("suma_valoracion_1", 145, 162, "valoracion"),
    FieldSpec("suma_valoracion_2", 163, 180, "valoracion"),
]

DETALLE_FIELDS = [
    FieldSpec("tipo_registro", 1, 1, "int"),
    FieldSpec("modelo", 2, 4, "str"),
    FieldSpec("ejercicio", 5, 8, "int"),
    FieldSpec("nif_declarante", 9, 17, "str"),
    FieldSpec("nif_declarado", 18, 26, "str"),
    FieldSpec("nif_representante", 27, 35, "str"),
    FieldSpec("nombre_razon_declarado", 36, 75, "str"),
    FieldSpec("clave_condicion", 76, 76, "int"),
    FieldSpec("tipo_titularidad_texto", 77, 101, "str"),
    FieldSpec("clave_tipo_bien", 102, 102, "enum", enum_class=ClaveBien),
    FieldSpec("subclave", 103, 103, "int"),
    FieldSpec("tipo_derecho_real_inmueble", 104, 128, "str"),
    FieldSpec("codigo_pais", 129, 130, "str"),
    FieldSpec("clave_identificacion", 131, 131, "int"),
    FieldSpec("identificacion_valores", 132, 143, "str"),
    FieldSpec("clave_ident_cuenta", 144, 144, "str"),
    FieldSpec("codigo_bic", 145, 155, "str"),
    FieldSpec("codigo_cuenta", 156, 189, "str"),
    FieldSpec("identificacion_entidad", 190, 230, "str"),
    FieldSpec("nif_entidad_pais_residencia", 231, 250, "str"),
    FieldSpec("domicilio_via_num", 251, 302, "str"),
    FieldSpec("domicilio_complemento", 303, 342, "str"),
    FieldSpec("domicilio_poblacion", 343, 372, "str"),
    FieldSpec("domicilio_region", 373, 402, "str"),
    FieldSpec("domicilio_cp", 403, 412, "str"),
    FieldSpec("domicilio_pais", 413, 414, "str"),
    FieldSpec("fecha_incorporacion", 415, 422, "date8", required=False),
    FieldSpec("origen", 423, 423, "enum", enum_class=Origen),
    FieldSpec("fecha_extincion", 424, 431, "date8", required=False),
    FieldSpec("valoracion_1", 432, 446, "valoracion"),
    FieldSpec("valoracion_2", 447, 461, "valoracion"),
    FieldSpec("clave_repr_valores", 462, 462, "str"),
    FieldSpec("numero_valores_entera", 463, 472, "int"),
    FieldSpec("numero_valores_decimal", 473, 474, "int"),
    FieldSpec("clave_tipo_bien_inmueble", 475, 475, "str"),
    FieldSpec("porcentaje_participacion_entera", 476, 478, "int"),
    FieldSpec("porcentaje_participacion_decimal", 479, 480, "int"),
]

class ParserFormatError(Exception):
    pass

class CSV720Error(Exception):
    pass


class Parser:
    """Parser and validator for Agencia Tributaria Modelo 720 fixed-width and CSV files."""
    
    def __init__(self, encoding: str = "latin-1"):
        self.encoding = encoding
    
    def _slice(self, line: str, start: int, end: int) -> str:
        """Extract substring from line using 1-based positions."""
        return line[start - 1 : end]
    
    def _to_int(self, s: str) -> int:
        """Convert string to integer, treating empty as 0."""
        s = s.strip()
        if not s:
            return 0
        if not re.fullmatch(r"[0-9]+", s):
            raise ValueError(f"Expected numeric, got {s!r}")
        return int(s)
    
    def _to_decimal_from_cents(self, sign_char: str, cents_str: str) -> Decimal:
        """Convert sign character and cents string to Decimal."""
        if not cents_str.strip():
            return Decimal("0.00")
        if not re.fullmatch(r"[0-9]+", cents_str):
            raise ValueError(f"Expected numeric cents, got {cents_str!r}")
        val = Decimal(int(cents_str)).scaleb(-2)
        if sign_char == "N":
            val = -val
        return val.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    
    def _to_date8(self, s: str) -> Optional[date]:
        """Convert 8-digit string to date, handling empty/zero cases."""
        s = s.strip()
        if not s or s == "00000000":
            return None
        if not re.fullmatch(r"[0-9]{8}", s):
            raise ValueError(f"Expected AAAAMMDD, got {s!r}")
        y, m, d = int(s[:4]), int(s[4:6]), int(s[6:8])
        return date(y, m, d)
    
    def _parse_field(self, line: str, field_spec: FieldSpec) -> any:
        """Parse a single field from a line based on field specification."""
        raw_value = self._slice(line, field_spec.start, field_spec.end)
        
        if field_spec.transform == "str":
            result = raw_value.rstrip() if raw_value else ""
            return result if result or not field_spec.required else (None if field_spec.required else "")
            
        elif field_spec.transform == "int":
            return self._to_int(raw_value)
            
        elif field_spec.transform == "date8":
            return self._to_date8(raw_value)
            
        elif field_spec.transform == "bool_c":
            return raw_value.strip() == "C"
            
        elif field_spec.transform == "bool_s":
            return raw_value.strip() == "S"
            
        elif field_spec.transform == "enum":
            stripped = raw_value.strip()
            return field_spec.enum_class(stripped) if stripped else None
            
        elif field_spec.transform == "valoracion":
            # Handle valoracion fields (sign + amount)
            # For fixed-width, this represents sign + 17 digits (valoracion uses positions like 145-162)
            sign_char = raw_value[0] if raw_value else " "
            amount_str = raw_value[1:] if len(raw_value) > 1 else ""
            return Valoracion(sign_char, self._to_decimal_from_cents(sign_char, amount_str))
            
        else:
            raise ValueError(f"Unknown transform type: {field_spec.transform}")
    
    def _parse_line(self, line: str, field_specs: List[FieldSpec]) -> dict:
        """Parse a line using field specifications."""
        result = {}
        for field_spec in field_specs:
            try:
                result[field_spec.name] = self._parse_field(line, field_spec)
            except Exception as e:
                raise ParserFormatError(f"Error parsing field '{field_spec.name}': {e}")
        return result
    
    def _parse_header(self, line: str) -> Header720:
        """Parse header line using field specifications."""
        fields = self._parse_line(line, HEADER_FIELDS)
        return Header720(**fields)
    
    def _parse_detalle(self, line: str) -> Detalle720:
        """Parse detail line using field specifications."""
        fields = self._parse_line(line, DETALLE_FIELDS)
        return Detalle720(**fields)
    
    def _iter_lines(self, path_or_stream: Union[str, Iterable[str]]) -> Iterable[str]:
        """Iterate over lines from file or stream."""
        if isinstance(path_or_stream, str):
            with open(path_or_stream, "r", encoding=self.encoding) as f:
                for ln in f:
                    yield ln.rstrip("\n\r")
        else:
            for ln in path_or_stream:
                yield ln.rstrip("\n\r")
    
    def read_fixed_width(self, path_or_stream: Union[str, Iterable[str]]) -> Declaration:
        """Read Modelo 720 from fixed-width format."""
        lines = [ln for ln in self._iter_lines(path_or_stream) if ln.strip()]
        header = self._parse_header(lines[0])
        detalles = [self._parse_detalle(ln) for ln in lines[1:]]
        return Declaration(header, detalles)
    
    def write_csv(self, declaration: Declaration, fp: Union[str, TextIO]):
        """Write declaration to CSV format."""
        import csv
        
        need_close = False
        if isinstance(fp, str):
            f = open(fp, "w", newline="", encoding="utf-8")
            need_close = True
        else:
            f = fp
        try:
            w = csv.writer(f)
            # Header section
            w.writerow(["__SECTION__", "HEADER"])
            w.writerow(["field", "value"])
            h = declaration.header
            for field_spec in HEADER_FIELDS:
                if field_spec.csv_include:
                    value = self._get_header_field_value(h, field_spec)
                    w.writerow([field_spec.name, value])
            
            # Details section  
            w.writerow(["__SECTION__", "DETALLES"])
            w.writerow([f.name for f in DETALLE_FIELDS if f.csv_include])
            for d in declaration.detalles:
                row = []
                for field_spec in DETALLE_FIELDS:
                    if field_spec.csv_include:
                        value = self._get_detalle_field_value(d, field_spec)
                        row.append(value)
                w.writerow(row)
        finally:
            if need_close:
                f.close()
    
    def _get_header_field_value(self, header: Header720, field_spec: FieldSpec) -> str:
        """Get string representation of header field for CSV."""
        v = getattr(header, field_spec.name)
        if isinstance(v, bool):
            return "1" if v else "0"
        elif isinstance(v, Valoracion):
            return str(v.importe)
        else:
            return "" if v is None else str(v)
    
    def _get_detalle_field_value(self, detalle: Detalle720, field_spec: FieldSpec) -> str:
        """Get string representation of detalle field for CSV."""
        v = getattr(detalle, field_spec.name)
        if isinstance(v, Enum):
            return v.value
        elif isinstance(v, date):
            return v.isoformat()
        elif isinstance(v, Valoracion):
            return str(v.importe)
        else:
            return "" if v is None else str(v)
    
    def read_csv(self, fp: Union[str, TextIO]) -> Declaration:
        """Read declaration from CSV format."""
        import csv
        
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
            header_start = next(i for i, row in enumerate(rows) if row[:2] == ["__SECTION__", "HEADER"]) + 1
            detalles_start = next(i for i, row in enumerate(rows) if row[:2] == ["__SECTION__", "DETALLES"]) + 1
        except StopIteration:
            raise CSV720Error("Missing __SECTION__ markers for HEADER/DETALLES")
        
        # Parse header section
        header_table = rows[header_start:detalles_start-1]
        if not header_table:
            raise CSV720Error("Empty header section")
        if header_table and header_table[0][:2] == ["field", "value"]:
            header_table = header_table[1:]
        
        hvals = {k: v for k, v, *_ in header_table}
        # Set defaults
        hvals.setdefault("tipo_registro", "1")
        hvals.setdefault("modelo", MODEL_CODE)
        
        header = self._parse_csv_header(hvals)
        
        # Parse details section
        det_header = rows[detalles_start]
        expected_columns = [f.name for f in DETALLE_FIELDS if f.csv_include]
        if det_header != expected_columns:
            raise CSV720Error("Detalles header row does not match expected columns")
        
        det_rows = rows[detalles_start+1:]
        detalles = []
        for ridx, row in enumerate(det_rows, start=1):
            if not any((c or '').strip() for c in row):
                continue
            vals = dict(zip(expected_columns, row))
            detalle = self._parse_csv_detalle(vals, ridx)
            detalles.append(detalle)
        
        dec = Declaration(header, detalles)
        try:
            dec.validate()
        except DeclarationValidationError as e:
            raise CSV720Error(str(e))
        return dec
    
    def write_fixed_width(self, declaration: Declaration, fp: Union[str, TextIO]):
        """Write declaration to fixed-width Modelo 720 format."""
        need_close = False
        if isinstance(fp, str):
            f = open(fp, "w", encoding="latin-1")
            need_close = True
        else:
            f = fp
        
        try:
            # Write header line
            header_line = self._format_header_line(declaration.header)
            f.write(header_line + "\n")
            
            # Write detail lines
            for detalle in declaration.detalles:
                detail_line = self._format_detalle_line(detalle)
                f.write(detail_line + "\n")
                
        finally:
            if need_close:
                f.close()
    
    def _format_header_line(self, header: Header720) -> str:
        """Format header record to fixed-width string."""
        line = ""
        for field_spec in HEADER_FIELDS:
            value = self._format_field_value(header, field_spec)
            line += value
        # Pad to exactly 500 characters as required by Spanish tax authority
        return line.ljust(500)
    
    def _format_detalle_line(self, detalle: Detalle720) -> str:
        """Format detail record to fixed-width string."""
        line = ""
        for field_spec in DETALLE_FIELDS:
            value = self._format_field_value(detalle, field_spec)
            line += value
        # Pad to exactly 500 characters as required by Spanish tax authority  
        return line.ljust(500)
    
    def _format_field_value(self, record: Union[Header720, Detalle720], field_spec: FieldSpec) -> str:
        """Format a single field value according to its field specification."""
        raw_value = getattr(record, field_spec.name)
        field_width = field_spec.end - field_spec.start + 1
        
        if field_spec.transform == "str":
            # String fields: left-aligned, padded with spaces
            value = str(raw_value) if raw_value is not None else ""
            return value.ljust(field_width)[:field_width]
            
        elif field_spec.transform == "int":
            # Integer fields: right-aligned, zero-padded
            value = str(raw_value) if raw_value is not None else "0"
            return value.zfill(field_width)
            
        elif field_spec.transform == "date8":
            # Date fields: AAAAMMDD format or 00000000 for None
            if raw_value is None:
                return "00000000"
            else:
                return raw_value.strftime("%Y%m%d")
                
        elif field_spec.transform == "bool_c":
            # Boolean fields (C for True, space for False)
            return "C" if raw_value else " "
            
        elif field_spec.transform == "bool_s":
            # Boolean fields (S for True, space for False)
            return "S" if raw_value else " "
            
        elif field_spec.transform == "enum":
            # Enum fields: use the enum value
            return raw_value.value if raw_value is not None else " "
            
        elif field_spec.transform == "valoracion":
            # Valoracion fields: sign + amount in cents (17 digits total)
            if raw_value is None:
                return " " + "0".zfill(field_width - 1)
            
            sign = raw_value.signo
            # Convert to cents (multiply by 100) and format as integer
            cents = int(raw_value.importe * 100)
            amount_str = str(cents).zfill(field_width - 1)
            return sign + amount_str
            
        else:
            raise ValueError(f"Unknown field transform: {field_spec.transform}")
    
    def _parse_csv_header(self, hvals: dict) -> Header720:
        """Parse header from CSV values."""
        def _parse_decimal_euros(s: str) -> Valoracion:
            s = (s or "").strip()
            if not s:
                return Valoracion(" ", Decimal("0.00"))
            d = Decimal(s)
            signo = "N" if d < 0 else " "
            return Valoracion(signo, abs(d).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
        
        def _str_to_bool(s: str) -> bool:
            s = (s or "").strip().lower()
            return s in {"1", "true", "t", "yes", "y", "si", "sí"}
        
        try:
            ejercicio = int(hvals.get("ejercicio", "0"))
        except Exception:
            raise CSV720Error("Header 'ejercicio' must be integer")
        
        numero_total_registros = int(hvals.get("numero_total_registros", "0") or "0")
        suma_val1 = _parse_decimal_euros(hvals.get("suma_valoracion_1", "0"))
        suma_val2 = _parse_decimal_euros(hvals.get("suma_valoracion_2", "0"))
        
        return Header720(
            tipo_registro=int(hvals.get("tipo_registro", "1")),
            modelo=hvals.get("modelo", MODEL_CODE),
            ejercicio=ejercicio,
            nif_declarante=(hvals.get("nif_declarante") or ""),
            nombre_razon=(hvals.get("nombre_razon") or ""),
            tipo_soporte=(hvals.get("tipo_soporte") or " "),
            telefono_contacto=hvals.get("telefono_contacto") or None,
            persona_contacto=hvals.get("persona_contacto") or None,
            numero_identificativo=(hvals.get("numero_identificativo") or ""),
            declaracion_complementaria=_str_to_bool(hvals.get("declaracion_complementaria", "")),
            declaracion_sustitutiva=_str_to_bool(hvals.get("declaracion_sustitutiva", "")),
            numero_identificativo_anterior=hvals.get("numero_identificativo_anterior") or None,
            numero_total_registros=numero_total_registros,
            suma_valoracion_1=suma_val1,
            suma_valoracion_2=suma_val2,
        )
    
    def _parse_csv_detalle(self, vals: dict, ridx: int) -> Detalle720:
        """Parse detalle from CSV values."""
        def _req_int(name: str) -> int:
            try:
                return int((vals.get(name) or "0").strip() or "0")
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
        
        def _str_field(name: str) -> str:
            s = (vals.get(name) or "").strip()
            # Get max length from field spec
            field_spec = next((f for f in DETALLE_FIELDS if f.name == name), None)
            if field_spec:
                maxlen = field_spec.end - field_spec.start + 1
                if len(s) > maxlen:
                    raise CSV720Error(f"Detail row {ridx}: field '{name}' exceeds max length {maxlen}")
            return s
        
        def _enum_field(enum_cls, name: str):
            s = (vals.get(name) or "").strip()
            if not s:
                raise CSV720Error(f"Detail row {ridx}: field '{name}' is required")
            try:
                return enum_cls(s)
            except Exception:
                raise CSV720Error(f"Detail row {ridx}: field '{name}' invalid value '{s}'")
        
        def _valor_field(name: str) -> Valoracion:
            s = (vals.get(name) or "").strip()
            if not s:
                return Valoracion(" ", Decimal("0.00"))
            d = Decimal(s)
            signo = "N" if d < 0 else " "
            return Valoracion(signo, abs(d).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
        
        return Detalle720(
            tipo_registro=_req_int("tipo_registro"),
            modelo=_str_field("modelo"),
            ejercicio=_req_int("ejercicio"),
            nif_declarante=_str_field("nif_declarante"),
            nif_declarado=_str_field("nif_declarado"),
            nif_representante=_str_field("nif_representante"),
            nombre_razon_declarado=_str_field("nombre_razon_declarado"),
            clave_condicion=_req_int("clave_condicion"),
            tipo_titularidad_texto=_str_field("tipo_titularidad_texto"),
            clave_tipo_bien=_enum_field(ClaveBien, "clave_tipo_bien"),
            subclave=_req_int("subclave"),
            tipo_derecho_real_inmueble=_str_field("tipo_derecho_real_inmueble"),
            codigo_pais=_str_field("codigo_pais"),
            clave_identificacion=_req_int("clave_identificacion"),
            identificacion_valores=_str_field("identificacion_valores"),
            clave_ident_cuenta=_str_field("clave_ident_cuenta"),
            codigo_bic=_str_field("codigo_bic"),
            codigo_cuenta=_str_field("codigo_cuenta"),
            identificacion_entidad=_str_field("identificacion_entidad"),
            nif_entidad_pais_residencia=_str_field("nif_entidad_pais_residencia"),
            domicilio_via_num=_str_field("domicilio_via_num"),
            domicilio_complemento=_str_field("domicilio_complemento"),
            domicilio_poblacion=_str_field("domicilio_poblacion"),
            domicilio_region=_str_field("domicilio_region"),
            domicilio_cp=_str_field("domicilio_cp"),
            domicilio_pais=_str_field("domicilio_pais"),
            fecha_incorporacion=_opt_date("fecha_incorporacion"),
            origen=_enum_field(Origen, "origen"),
            fecha_extincion=_opt_date("fecha_extincion"),
            valoracion_1=_valor_field("valoracion_1"),
            valoracion_2=_valor_field("valoracion_2"),
            clave_repr_valores=_str_field("clave_repr_valores"),
            numero_valores_entera=_req_int("numero_valores_entera"),
            numero_valores_decimal=_req_int("numero_valores_decimal"),
            clave_tipo_bien_inmueble=_str_field("clave_tipo_bien_inmueble"),
            porcentaje_participacion_entera=_req_int("porcentaje_participacion_entera"),
            porcentaje_participacion_decimal=_req_int("porcentaje_participacion_decimal"),
        )