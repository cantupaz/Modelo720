from Modelo720 import Parser, DeclarationValidationError


parser = Parser()

# Read fixed-width file
dec = parser.read_fixed_width("example.720")
try:
    dec.validate()
    print("Valid! Declarant:", dec.header.nif_declarante)
except DeclarationValidationError as e:
    print(f"Invalid file: {e}")

# Write to CSV
parser.write_csv(dec, "example.csv")

# Read back from CSV
dec2 = parser.read_csv("example.csv")

# Write back to fixed-width
parser.write_fixed_width(dec2, "example-rewritten.720")

dec2 = parser.read_fixed_width("example-rewritten.720")
if dec == dec2:
    print("Declarations are equal after round-trip conversion.")
else:
    raise RuntimeError("Declarations differ after round-trip conversion.")

dec2.print_declaration()
