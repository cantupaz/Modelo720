from modelo720 import read_modelo720, validate, to_dict

dec = read_modelo720("Y1234567Z.720")
problems = validate(dec)
if problems:
    print("Invalid file:\n - " + "\n - ".join(problems))
else:
    print("Valid! Declarant:", dec.header.nif_declarante)
    data = to_dict(dec)  # JSON-friendly structure

print(dec)