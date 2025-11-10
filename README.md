# Modelo720

A Python library for parsing and writing Spanish tax authority Modelo 720 declaration files.

## Overview

Modelo720 provides a clean, type-safe interface for working with Spanish tax form 720 files, which are used to declare foreign assets. The library supports both the official fixed-width format used by the Agencia Tributaria and a proprietary CSV format for easier data entry and analysis.

## Features

- **Read/Write Fixed-Width Files**: Parse official Modelo 720 `.720` files
- **Read/Write CSV Files**: Convert to/from a human-readable CSV format
- **Data Validation**: Comprehensive validation of declaration data
- **Type Safety**: Full type hints and dataclass-based models
- **Round-Trip Accuracy**: Perfect fidelity between formats
- **Clean API**: Simple, intuitive interface following Python conventions

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from Modelo720 import Parser, Declaration

# Create a parser instance
parser = Parser()

# Read a fixed-width Modelo 720 file
declaration = parser.read_fixed_width("my_declaration.720")

# Validate the declaration
try:
    declaration.validate()
    print("✓ Declaration is valid")
except DeclarationValidationError as e:
    print(f"✗ Validation failed: {e}")

# Convert to CSV for easier viewing/editing
parser.write_csv(declaration, "declaration.csv")

# Read back from CSV
declaration2 = parser.read_csv("declaration.csv")

# Write back to official format
parser.write_fixed_width(declaration2, "output.720")
```

## API Reference

### Parser Class

The main `Parser` class provides methods for reading and writing declarations:

```python
parser = Parser(encoding="latin-1")  # Default encoding for .720 files
```

#### Methods

- **`read_fixed_width(file_path)`** - Read official .720 format
- **`write_fixed_width(declaration, file_path)`** - Write official .720 format  
- **`read_csv(file_path)`** - Read proprietary CSV format
- **`write_csv(declaration, file_path)`** - Write proprietary CSV format

### Data Models

The library uses dataclasses to represent the declaration structure:

- **`Declaration`** - Complete tax declaration
- **`Header720`** - Header record with declarant information
- **`Detalle720`** - Detail record for each asset
- **`Valoracion`** - Monetary value with sign

### Validation

Declarations can be validated using the `validate()` method:

```python
try:
    declaration.validate()
except DeclarationValidationError as e:
    # Handle validation errors
    print(f"Validation failed: {e}")
```

Validation includes:
- Structural validation (required fields, formats)
- Business rule validation (asset type constraints)
- Financial validation (sum totals must match)

## File Formats

### Fixed-Width Format (.720)

The official format used by the Spanish tax authority:
- 500 character fixed-width lines
- Latin-1 encoding
- Specific field positions and formats
- Header line followed by detail lines

### CSV Format

A proprietary CSV format for easier data manipulation:
- UTF-8 encoding
- Section-based structure (`__SECTION__` markers)
- Human-readable field names
- ISO date formats

## Examples

### Basic Usage

```python
from Modelo720 import Parser

parser = Parser()

# Read and validate
declaration = parser.read_fixed_width("input.720")
declaration.validate()

# Print summary
print(f"Declarant: {declaration.header.nif_declarante}")
print(f"Assets: {len(declaration.detalles)}")
print(f"Total value: {declaration.header.suma_valoracion_1.importe}€")
```

### Converting Formats

```python
# Convert .720 to CSV
declaration = parser.read_fixed_width("input.720")
parser.write_csv(declaration, "output.csv")

# Convert CSV back to .720
declaration = parser.read_csv("input.csv")
parser.write_fixed_width(declaration, "output.720")
```

### Asset Information

```python
# Print details about each declared asset
for i, asset in enumerate(declaration.detalles, 1):
    print(f"Asset {i}:")
    print(f"  Type: {asset.clave_tipo_bien.value}")
    print(f"  Country: {asset.codigo_pais}")
    print(f"  Value: {asset.valoracion_1.importe}€")
    print(f"  Owner: {asset.nombre_razon_declarado}")
```

## Error Handling

The library defines specific exception types:

- **`DeclarationValidationError`** - Validation failures
- **`ParserFormatError`** - Fixed-width format parsing errors
- **`CSV720Error`** - CSV format parsing errors

```python
from Modelo720 import Parser, DeclarationValidationError, ParserFormatError

try:
    declaration = parser.read_fixed_width("file.720")
    declaration.validate()
except ParserFormatError as e:
    print(f"File format error: {e}")
except DeclarationValidationError as e:
    print(f"Validation error: {e}")
```

## Development

### Running Tests

```bash
python -m unittest test_modelo720.py -v
```

### Project Structure

```
Modelo720/
├── Modelo720/
│   ├── __init__.py          # Package exports
│   ├── parser.py            # Main Parser class
│   └── declaracion.py       # Data models and validation
├── main.py                  # Example usage
├── test_modelo720.py        # Unit tests
└── README.md               # This file
```

## Asset Types

The library supports all Modelo 720 asset types:

- **C** - Bank accounts and credit (Cuentas bancarias)
- **V** - Securities and rights (Valores y derechos)  
- **I** - Real estate (Inmuebles)
- **S** - Insurance (Seguros)
- **B** - Movable goods (Bienes muebles)

## Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `python -m unittest test_modelo720.py`
2. Code follows existing style conventions
3. New features include appropriate tests
4. Documentation is updated for API changes

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Related

- [Agencia Tributaria](https://www.agenciatributaria.es/) - Spanish tax authority
- [Modelo 720 Information](https://www.agenciatributaria.es/AEAT.internet/en_gb/Inicio/Ayuda/Manuales__Folletos_y_Videos/Manuales_practicos/Modelo_720/Modelo_720.shtml) - Official documentation