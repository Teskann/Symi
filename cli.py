"""
Command-line interface of Symi
"""

from expr2sympy import expr2sympy, sub_num
import libs
from sympy import pprint, pprint_try_use_unicode, nsimplify, simplify, solve
import readline
import traceback


class AutoCompleter(object):
    """
    Custom auto completer
    """

    def __init__(self, options, variables):
        self.options = sorted(options.keys())
        self.variables = sorted(variables.keys())

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options
                                if s and s.startswith(text)] + [s for s in
                                                                self.variables
                                                                if text in s]
            else:  # no text entered, all matches possible
                self.matches = self.options[:] + self.variables

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


def update_completer(options, variables):
    """
    Update the auto completer with the new variables and options.
    Parameters
    ----------
    options : dict
        Symi options
    variables : dict
        Symi variables

    Returns
    -------
    None.
    """
    completer = AutoCompleter(options, variables)
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def perr(string):
    """
    Prints the string as an error

    Parameters
    ----------
    string : str
        Error description

    Returns
    -------
    str:
        Error description
    """

    print(f"{bcolors.FAIL}[ ERROR ] {string}{bcolors.ENDC}")


if __name__ == "__main__":
    uni = pprint_try_use_unicode()
    variables = {}
    options = {"implicit_multiplication": True,
               "num_tolerance": 1e-10}
    update_completer(options, variables)
    while 1:
        try:
            line = input("\nsymi> ").strip()

            if line == "":
                continue

            print("")

            # Show variables ..................................................

            if line == "vars":
                print(variables)
                continue

            # Show options ....................................................

            if line == "options":
                print(options)
                continue

            # Clear variables .................................................

            if line == "clear":
                variables = {}
                continue

            # Update options ..................................................

            if line.split(" ")[0] in options:
                if line.split(" ")[0] in ["implicit_multiplication"]:
                    try:
                        val = line.split(" ")[1].lower() in ['on', 'true', '1']
                        options[line.split(" ")[0]] = val
                    except IndexError:
                        perr(f"Error updating option "
                             f"{line.split(' ')[0]}. Please follow the syntax "
                             f":\n"
                             f"symi > {line.split(' ')[0]} on/off")
                    continue
                elif line.split(" ")[0] in ["num_tolerance"]:
                    try:
                        val = eval(line.split(" ")[1])
                        options[line.split(" ")[0]] = val
                    except (IndexError, NameError):
                        perr(f"Error updating option "
                             f"{line.split(' ')[0]}. Please follow the syntax "
                             f":\n"
                             f"symi > {line.split(' ')[0]} value")
                    continue

            # Import ..........................................................

            if line.split(" ")[0] == "import":
                try:
                    if line.split(" ")[1].lower() == 'physics_constants':
                        variables = {**variables, **libs.physics_constants}
                    else:
                        perr(f"Error importing package "
                             f"{line.split(' ')[0]}. Please use a valid "
                             f"package "
                             f"name")
                except IndexError:
                    perr(f"Syntax error. "
                         f"{line.split(' ')[0]}. Please follow the syntax :\n"
                         f"symi> import package")
                continue

            # Exit ............................................................

            if line.strip().lower() == "exit":
                print("Thanks for using Symi ! See you later !")
                break

            # Substitution ....................................................

            if line[-2:] == "!!":
                num = True
                line = line[:-1]
            else:
                num = False
            if line[-1] == "!":
                sub = True
                line = line[:-1]
            else:
                sub = False

            # Solve Equation ..................................................

            if '?' in line:
                eqns_list, vars_list = line.split("?")
                eqns = eqns_list.split(";")
                vars_list = vars_list.replace(',', '').replace(';', '')
                varss = vars_list.strip().split(' ')
                tru_eqns = []
                for eqn in eqns:
                    left, right = eqn.split("=")
                    if right.strip() in ['inf', 'oo', '-inf', '-oo']:
                        sign = '-' if '-' in right.strip() else ""
                        tru_eqns.append(expr2sympy(f"{sign}1/({left})",
                                                   options,
                                                   variables))
                    elif left.strip() in ['inf', 'oo', '-inf', '-oo']:
                        sign = '-' if '-' in left.strip() else ""
                        tru_eqns.append(expr2sympy(f"{sign}1/({right})",
                                                   options,
                                                   variables))
                    else:
                        lft = expr2sympy(left, options, variables)
                        rht = expr2sympy(right, options, variables)
                        tru_eqns.append(lft-rht)

                tru_vars = [expr2sympy(x, options, variables) for x in varss
                            if x.strip() != '']
                sol = solve(tru_eqns, tru_vars)
                pprint(sol)
                continue

            # Affectation .....................................................

            if "=" in line:
                var_name = expr2sympy(line.split("=")[0], options, variables)
                var_val = expr2sympy(line.split("=")[1], options, variables)

                variables[str(var_name)] = sub_num(var_val,
                                                   options, variables, sub,
                                                   num)
                update_completer(options, variables)

            # Show Result .....................................................

            else:
                if line in variables:
                    pprint(sub_num(variables[line], options, variables, sub,
                                   num))
                    continue
                sym = simplify(sub_num(expr2sympy(line, options, variables),
                               options, variables, sub, num))
                pprint(sym)

                variables["ans_"] = sym

        except KeyboardInterrupt:
            print("Thanks for using Symi ! See you later !")
            break

        except Exception:
            print(bcolors.FAIL)
            traceback.print_exc()
            print(bcolors.ENDC)