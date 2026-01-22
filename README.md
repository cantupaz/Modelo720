# Modelo720

A Python library for parsing and writing Spanish tax authority Modelo 720 declaration files.

## Overview

Modelo720 provides a type-safe interface for working with Spanish tax form 720 files, which are used to declare foreign assets. The library supports both the official fixed-width format used by the Agencia Tributaria and a proprietary CSV format for easier data entry.

## Features

- **Read/Write Fixed-Width Files**: Parse official Modelo 720 `.720` files
- **Read/Write CSV Files**: Convert to/from a human-readable CSV format
- **Data Validation**: Comprehensive validation of declaration data
- **Type Safety**: Full type hints and dataclass-based models

## Installation

### From Source

```bash
git clone https://github.com/cantupaz/Modelo720.git
cd Modelo720
pip install -e .
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
    print("Declaration is valid")
except DeclarationValidationError as e:
    print(f"Validation failed: {e}")

# Convert to CSV for easier viewing/editing
parser.write_csv(declaration, "declaration.csv")

## at this point you can edit declaration.csv to update positions or dates

# Read back from CSV
declaration2 = parser.read_csv("declaration.csv")

# Write back to official format
parser.write_fixed_width(declaration2, "output.720")
```

## API Reference

### Parser Class

The main `Parser` class provides methods for reading and writing declarations:

```python
parser = Parser()
```

#### Methods

- **`read_fixed_width(file_path: str) -> Declaration`** - Read official .720 format
- **`write_fixed_width(declaration: Declaration, file_path: str)`** - Write official .720 format
- **`read_csv(file_path: str) -> Declaration`** - Read proprietary CSV format
- **`write_csv(declaration: Declaration, file_path: str)`** - Write proprietary CSV format

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
- Validation of asset type constraints
- Financial validation (sum totals must match)

## File Formats

### Fixed-Width Format (.720)

The official format used by the Agencia Tributaria:

- 500 character fixed-width lines
- Type 1: Header record (one per file)
- Type 2: Detail records (one per asset)

The format is documented in the BOE (https://www.boe.es/buscar/act.php?id=BOE-A-2013-954#an) and
the `modelo_720.pdf`

### CSV Format

A more human-readable format for data entry:

- Header row with column names
- One row per declaration component
- Easier to edit in spreadsheet software

## Examples

See the `example.720` and `example.csv` files in the repository for sample data, and `main.py` for a complete usage example.

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=Modelo720 --cov-report=html
```

## Development

This is a pure Python library with no external runtime dependencies except Pydantic. For development:

1. Clone the repository
2. Install with dev dependencies: `pip install -e ".[dev]"`
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Before submitting a Pull Request, please open an issue and we can discuss.

## Support

For issues and questions, please use the GitHub issue tracker.
