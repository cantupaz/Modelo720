from Modelo720 import Parser, DeclarationValidationError

# Create parser instance
parser = Parser()

# Read fixed-width file 
dec = parser.read_fixed_width("Y1234567Z.720")
try:
    dec.validate()
    print("Valid! Declarant:", dec.header.nif_declarante)
except DeclarationValidationError as e:
    print(f"Invalid file: {e}")

# Write to CSV
parser.write_csv(dec, "output.csv")

# Read back from CSV
dec2 = parser.read_csv("output.csv")

# Write back to fixed-width
parser.write_fixed_width(dec2, "output_rewritten.720")

dec2 = parser.read_fixed_width("output_rewritten.720")
if dec == dec2:
    print("Declarations are equal after round-trip conversion.")
else:
    print("Declarations differ after round-trip conversion.")

# dec2.print_declaration()

