"""
Command-line interface of Symi
"""

from expr2sympy import expr2sympy, subs
from sympy import pprint, pprint_try_use_unicode

if __name__ == "__main__":
    uni = pprint_try_use_unicode()
    variables = {}
    while 1:
        line = input("symi > ").strip()

        if line == "vars":
            print(variables)
            continue

        # Exit ...............................................................

        if line.strip().lower() == "exit":
            print("Thanks for using Symi ! See you later !")
            break

        # Substitution .......................................................

        if line[-1] == "!":
            sub = True
            line = line[:-1]
        else:
            sub = False

        # Affectation ........................................................

        if "=" in line:
            var_name = expr2sympy(line.split("=")[0])
            var_val = expr2sympy(line.split("=")[1])
            if sub:
                var_val = subs(var_val, variables)
            variables[str(var_name)] = var_val

        # Show Result ........................................................

        else:
            sym = expr2sympy(line)
            if sub:
                sym = subs(sym, variables)
            pprint(sym.simplify(), use_unicode=False)


