from Modelo720.modelo720 import Modelo720, to_dict

# Create parser instance
parser = Modelo720()

# Read fixed-width file 
dec = parser.read_fixed_width("Y1234567Z.720")
problems = dec.validate()
if problems:
    print("Invalid file:\n - " + "\n - ".join(problems))
else:
    print("Valid! Declarant:", dec.header.nif_declarante)
    data = to_dict(dec)  # JSON-friendly structure

# # Write to CSV
parser.write_csv(dec, "output.csv")

# Read back from CSV
dec2 = parser.read_csv("output.csv")

print("declaraciones iguales?", dec == dec2)

dec2.print_declaration()

