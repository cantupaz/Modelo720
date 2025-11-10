from Modelo720.modelo720 import read_modelo720, validate, to_dict, print_declaration, write_csv, read_csv

dec = read_modelo720("Y1234567Z.720")
problems = validate(dec)
if problems:
    print("Invalid file:\n - " + "\n - ".join(problems))
else:
    print("Valid! Declarant:", dec.header.nif_declarante)
    data = to_dict(dec)  # JSON-friendly structure


# print_declaration(dec)
write_csv(dec, "output.csv")

dec = read_csv("output.csv")
print_declaration(dec)