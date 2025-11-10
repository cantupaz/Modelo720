from Modelo720 import Modelo720, DeclarationValidationError

# Create parser instance
parser = Modelo720()

# Read fixed-width file 
dec = parser.read_fixed_width("Y1234567Z.720")
try:
    dec.validate()
    print("Valid! Declarant:", dec.header.nif_declarante)
except DeclarationValidationError as e:
    print(f"Invalid file: {e}")

# # Write to CSV
parser.write_csv(dec, "output.csv")

# Read back from CSV
dec2 = parser.read_csv("output.csv")

print("declaraciones iguales?", dec == dec2)

dec2.print_declaration()

