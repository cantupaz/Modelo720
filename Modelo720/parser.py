"""
Parser and Writer for Agencia Tributaria Modelo 720 fixed-width and proprietary CSV files.

The fixed-width format is the official format used by the Agencia Tributaria
for Modelo 720 declarations.

The proprietary CSV format is an alternative format that is intended as an easy way
to enter and read data. The CSV format preserves all data fields and structure.

"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_DOWN
from enum import Enum
from typing import List, Optional, Union
import csv
import re

from .declaracion import (
    Declaration,
    ClaveBien,
    Origen,
    Valoracion,
    Header720,
    Detalle720,
    DeclarationValidationError,
)


@dataclass
class FieldSpec:
    """Specification for a field in the Modelo 720 format."""

    name: str
    start: int  # 1-based position in fixed-width line
    end: int  # 1-based position in fixed-width line
    transform: str  # type: "int", "str", "date8", "decimal_cents", "bool_c", "bool_s", "enum"
    enum_class: Optional[type] = None  # For enum transforms


# Field specifications preserving exact current order and positions
HEADER_FIELDS = [
    FieldSpec("tipo_registro", 1, 1, "int"),
    FieldSpec("modelo", 2, 4, "str"),
    FieldSpec("ejercicio", 5, 8, "int"),
    FieldSpec("nif_declarante", 9, 17, "str"),
    FieldSpec("nombre_razon", 18, 57, "str"),
    FieldSpec("tipo_soporte", 58, 58, "str"),
    FieldSpec("telefono_contacto", 59, 67, "str"),
    FieldSpec("persona_contacto", 68, 107, "str"),
    FieldSpec("numero_identificativo", 108, 120, "str"),
    FieldSpec("declaracion_complementaria", 121, 121, "bool_c"),
    FieldSpec("declaracion_sustitutiva", 122, 122, "bool_s"),
    FieldSpec("numero_identificativo_anterior", 123, 135, "str"),
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
    FieldSpec("fecha_incorporacion", 415, 422, "date8"),
    FieldSpec("origen", 423, 423, "enum", enum_class=Origen),
    FieldSpec("fecha_extincion", 424, 431, "date8"),
    FieldSpec("valoracion_1", 432, 446, "valoracion"),
    FieldSpec("valoracion_2", 447, 461, "valoracion"),
    FieldSpec("clave_repr_valores", 462, 462, "str"),
    FieldSpec("numero_valores_entera", 463, 472, "int"),
    FieldSpec("numero_valores_decimal", 473, 474, "int"),
    FieldSpec("clave_tipo_bien_inmueble", 475, 475, "str"),
    FieldSpec("porcentaje_participacion_entera", 476, 478, "int"),
    FieldSpec("porcentaje_participacion_decimal", 479, 480, "int"),
]


class CSV720Error(Exception):
    """Exception raised for errors in the CSV 720 format."""


class Parser:
    """Parser and validator for Agencia Tributaria Modelo 720 fixed-width and CSV files."""

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
        raw_value = line[field_spec.start - 1 : field_spec.end]
        return self._parse_raw_value(raw_value, field_spec)

    def _parse_raw_value(self, raw_value: str, field_spec: FieldSpec) -> any:
        if field_spec.transform == "str":
            return raw_value.rstrip() if raw_value else ""

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
            # For fixed-width, this represents sign + 17 digits
            # (valoracion uses positions like 145-162)
            sign_char = raw_value[0] if raw_value else " "
            amount_str = raw_value[1:] if len(raw_value) > 1 else ""
            return Valoracion(
                signo=sign_char,
                importe=self._to_decimal_from_cents(sign_char, amount_str),
            )

        else:
            raise ValueError(f"Unknown transform type: {field_spec.transform}")

    def _parse_line(self, line: str, field_specs: List[FieldSpec]) -> dict:
        """Parse a line using field specifications."""
        result = {}
        for field_spec in field_specs:
            try:
                result[field_spec.name] = self._parse_field(line, field_spec)
            except Exception as e:
                msg = f"Error parsing field '{field_spec.name}': {e}"
                raise ValueError(msg) from e
        return result

    def _parse_header(self, line: str) -> Header720:
        """Parse header line using field specifications."""
        fields = self._parse_line(line, HEADER_FIELDS)
        return Header720(**fields)

    def _parse_detalle(self, line: str) -> Detalle720:
        """Parse detail line using field specifications."""
        fields = self._parse_line(line, DETALLE_FIELDS)
        return Detalle720(**fields)

    def read_fixed_width(self, file_path: str) -> Declaration:
        """Read Modelo 720 from fixed-width format."""
        with open(file_path, "r", encoding="ISO-8859-1") as f:
            lines = [ln.rstrip("\n\r") for ln in f if ln.strip()]
        header = self._parse_header(lines[0])
        detalles = [self._parse_detalle(ln) for ln in lines[1:]]
        return Declaration(header=header, detalles=detalles)

    def write_fixed_width(self, declaration: Declaration, file_path: str):
        """Write declaration to fixed-width Modelo 720 format."""
        with open(file_path, "w", encoding="ISO-8859-1") as f:
            header_line = self._format_record_line(declaration.header, HEADER_FIELDS)
            f.write(header_line + "\n")

            for detalle in declaration.detalles:
                detail_line = self._format_record_line(detalle, DETALLE_FIELDS)
                f.write(detail_line + "\n")

    def _format_record_line(
        self, record: Union[Header720, Detalle720], field_specs: List[FieldSpec]
    ) -> str:
        """Format a record to fixed-width string using the provided field specifications."""
        line = ""
        for field_spec in field_specs:
            value = self._format_field_value(record, field_spec)
            line += value
        # Pad to exactly 500 characters
        return line.ljust(500)

    def _format_field_value(
        self, record: Union[Header720, Detalle720], field_spec: FieldSpec
    ) -> str:
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

    def write_csv(self, declaration: Declaration, file_path: str):
        """Write declaration to CSV format."""

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            # Header section
            w.writerow(["__SECTION__", "HEADER"])
            w.writerow(["field", "value"])
            h = declaration.header
            for field_spec in HEADER_FIELDS:
                value = self._get_field_value_for_csv(h, field_spec)
                w.writerow([field_spec.name, value])

            # Details section
            w.writerow(["__SECTION__", "DETALLES"])
            w.writerow([f.name for f in DETALLE_FIELDS])
            for d in declaration.detalles:
                row = []
                for field_spec in DETALLE_FIELDS:
                    value = self._get_field_value_for_csv(d, field_spec)
                    row.append(value)
                w.writerow(row)

    def _get_field_value_for_csv(
        self, record: Union[Header720, Detalle720], field_spec: FieldSpec
    ) -> str:
        """Get string representation of field for CSV."""
        v = getattr(record, field_spec.name)
        if isinstance(v, bool):
            return "1" if v else "0"
        elif isinstance(v, Enum):
            return v.value
        elif isinstance(v, date):
            return v.isoformat()
        elif isinstance(v, Valoracion):
            return str(v.importe)
        else:
            return "" if v is None else str(v)

    def read_csv(self, file_path: str) -> Declaration:
        """Read declaration from CSV format."""

        with open(file_path, "r", newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            rows = list(r)

        try:
            header_start = (
                next(
                    i
                    for i, row in enumerate(rows)
                    if row[:2] == ["__SECTION__", "HEADER"]
                )
                + 1
            )
            detalles_start = (
                next(
                    i
                    for i, row in enumerate(rows)
                    if row[:2] == ["__SECTION__", "DETALLES"]
                )
                + 1
            )
        except StopIteration as exc:
            raise CSV720Error(
                "Missing __SECTION__ markers for HEADER/DETALLES"
            ) from exc

        # Parse header section
        header_table = rows[header_start : detalles_start - 1]
        if not header_table:
            raise CSV720Error("Empty header section")
        if header_table and header_table[0][:2] == ["field", "value"]:
            header_table = header_table[1:]

        hvals = {k: v for k, v, *_ in header_table}

        # Parse header using field specifications
        header_fields = self._parse_csv_line(hvals, HEADER_FIELDS)
        header = Header720(**header_fields)

        # Parse details section
        det_header = rows[detalles_start]
        expected_columns = [f.name for f in DETALLE_FIELDS]
        if det_header != expected_columns:
            raise CSV720Error("Detalles header row does not match expected columns")

        det_rows = rows[detalles_start + 1 :]
        detalles = []
        for ridx, row in enumerate(det_rows, start=1):
            if not any((c or "").strip() for c in row):
                continue
            vals = dict(zip(expected_columns, row))
            try:
                # Parse detail using field specifications
                detalle_fields = self._parse_csv_line(vals, DETALLE_FIELDS)
                detalle = Detalle720(**detalle_fields)
                detalles.append(detalle)
            except CSV720Error:
                raise
            except Exception as e:
                raise CSV720Error(f"Error parsing detail row {ridx}: {e}") from e

        dec = Declaration(header=header, detalles=detalles)
        try:
            dec.validate()
        except DeclarationValidationError as e:
            raise CSV720Error(str(e)) from e
        return dec

    def _parse_valoracion_from_string(self, s: str) -> Valoracion:
        """Parse a Valoracion from a string value."""
        s = (s or "").strip()
        if not s:
            return Valoracion(signo=" ", importe=Decimal("0.00"))
        d = Decimal(s)
        signo = "N" if d < 0 else " "
        return Valoracion(
            signo=signo, importe=abs(d).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        )

    def _parse_csv_field(self, csv_value: str, field_spec: FieldSpec) -> any:
        """Parse a CSV field value based on field specification."""
        csv_value = (csv_value or "").strip()

        if field_spec.transform == "date8":
            if not csv_value:
                return None
            try:
                return date.fromisoformat(csv_value)
            except ValueError as e:
                raise ValueError(
                    f"Expected YYYY-MM-DD date for field '{field_spec.name}', got {csv_value!r}"
                ) from e

        elif field_spec.transform == "bool_c":
            return csv_value.lower() in {"1", "true", "t", "yes", "y", "si", "sí"}

        elif field_spec.transform == "bool_s":
            return csv_value.lower() in {"1", "true", "t", "yes", "y", "si", "sí"}

        elif field_spec.transform == "valoracion":
            return self._parse_valoracion_from_string(csv_value)

        else:
            # all other types
            return self._parse_raw_value(csv_value, field_spec)

    def _parse_csv_line(self, csv_values: dict, field_specs: List[FieldSpec]) -> dict:
        """Parse CSV values using field specifications."""
        result = {}
        for field_spec in field_specs:
            try:
                csv_value = csv_values.get(field_spec.name, "")
                result[field_spec.name] = self._parse_csv_field(csv_value, field_spec)
            except Exception as e:
                msg = f"Error parsing CSV field '{field_spec.name}': {e}"
                raise CSV720Error(msg) from e
        return result
