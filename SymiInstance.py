import readline
from collections import Iterable
from os.path import join, dirname, abspath


# Color the output ____________________________________________________________
from sympy import simplify, parse_expr, pprint, pprint_try_use_unicode, Symbol, \
    limit, solve, pretty

import libs
from colors import bcolors
from expr2sympy import expr2sympy, sub_num


# Auto Completer ______________________________________________________________

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
                self.matches = [s for s in self.options if s and s.startswith(text)] + [s for s in self.variables if text in s]
            else:  # no text entered, all matches possible
                self.matches = self.options[:] + self.variables

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


# Symi Instance _______________________________________________________________

class SymiInstance:
    """
    Instantiate this to create a Symi instance in your CLI

    Attributes
    ----------

    options: dict
        Symi options dict. Contains the following keys:
            "implicit_multiplication",
            "num_tolerance",
            "integration_variable",
            "diff_variable",
            "tau_kills_pi",
            "always_sub",
            "always_num"

    variables: dict of Sympy expressions
        Contains the variables saved by the user
    """

    PS1 = "\nsymi> "
    welcome_msg = """
  _____                 _ 
 / ____|               (_)
| (___  _   _ _ __ ___  _ 
 \___ \| | | | '_ ` _ \| |
 ____) | |_| | | | | | | |
|_____/ \__, |_| |_| |_|_|
         __/ |            
        |___/    Sympy CLI
"""[1:-1]

    # Constructor .............................................................

    def __init__(self):
        """Class constructor. Read class docstring for more details"""

        pprint_try_use_unicode()
        self.variables = {}
        self.options = {
            "implicit_multiplication": True,
            "num_tolerance": 1e-10,
            "integration_variable": None,
            "diff_variable": None,
            "tau_kills_pi": False,
            "always_sub": False,
            "always_num": False}
        self.update_completer()

        self.sub = False
        self.num = False

        # History . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        path = join(dirname(abspath(__file__)), ".symi_history")
        try:
            with open(path, "r") as f:
                readline.clear_history()
                history = f.readlines()
                for his in history:
                    his = his.strip()
                    if his == "":
                        continue
                    readline.add_history(his)
        except FileNotFoundError:
            pass

        print(self.welcome_msg)

    # Update Completer ........................................................

    def update_completer(self):
        """
        Update the auto completer with the new variables and options.

        Returns
        -------
        None.
        """
        completer = AutoCompleter(self.options, self.variables)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

    # Print output ............................................................

    def print(self, expr):
        """
        Print the expression with Sympy pretty

        Parameters
        ----------
        expr : Sympy Expression
            Expression to print
        """
        def recursive_subs(obj):
            if isinstance(obj, dict):
                for o in obj:
                    obj[o] = recursive_subs(obj[o])
                return obj
            elif isinstance(obj, Iterable):
                obj = list(obj)
                for i, o in enumerate(obj):
                    obj[i] = recursive_subs(o)
                return obj
            else:
                obj = simplify(obj.subs(parse_expr("tau"), parse_expr("2*pi")))
                obj = obj.subs(parse_expr("pi"), parse_expr("tau/2"))
                return obj

        if self.options["tau_kills_pi"]:
            expr = recursive_subs(expr)
        result = pretty(expr)
        if len(result.split('\n')) > 1:
            print('')
            print(result)
        else:
            print(result)

    # Print an error ..........................................................

    def perr(self, string):
        """
        Prints the string as an error

        Parameters
        ----------
        string : str
            Error description

        Returns
        -------
        status : int
            -1 (error)
        """

        print(f"{bcolors.FAIL}[ ERROR ] {string}{bcolors.ENDC}")
        return -1

    # Exit ....................................................................

    def exit(self):
        """
        Display an exit message and save the history.
        """
        print("Thanks for using Symi ! See you later !")
        path = join(dirname(abspath(__file__)), ".symi_history")
        with open(path, "w+") as f:
            history = f.readlines()
            for i in range(readline.get_current_history_length()):
                history.append(readline.get_history_item(i + 1))
            f.write('\n'.join(history[-1000:]))

    # Expression => Sympy .....................................................

    def expr2sympy(self, expr):
        """
        Convert the expression to Sympy. For more details check out the docstr
        of expr2sympy.expr2sympy function.

        Parameters
        ----------
        expr : str
            Expression to convert to sympy

        Returns
        -------

        sym_expr : Sympy Expression
            expr converted to Sympy
        """
        return expr2sympy(expr, self.options, self.variables, self.sub)

    # Substitution ............................................................

    def sub_num(self, expr):
        """
        Make the substitution and/or the numerical application.

        For more details, check the docstring of expr2sympy.sub_num()
        Parameters
        ----------
        expr : Sympy Expression

        Returns
        -------

        updated_expression : Sympy Expression
            Updated expression
        """

        def recursive_subs(obj):
            if isinstance(obj, dict):
                for o in obj:
                    obj[o] = recursive_subs(obj[o])
                return obj
            elif isinstance(obj, Iterable):
                obj = list(obj)
                for i, o in enumerate(obj):
                    obj[i] = recursive_subs(o)
                return obj
            else:
                return sub_num(obj, self.options, self.variables, self.sub, self.num)
        return recursive_subs(expr)

    # Parse line ..............................................................

    def parse_line(self, line):
        """
        Parse a Symi command line and process it.

        Special commands:
            - "vars" : display the user-stored variables
            - "options": display Symi options
            - "clear": clear all Symi variables
            - "exit": exit Symi
            - "import": To import variables

        Parameters
        ----------
        line : str
            Symi command line

        Returns
        -------

        status : int
            1 : Continue
            -1 : error
            0 : exit
        """

        line = line.strip()

        # Empty line  . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line == "":
            return 1

        # Show variables  . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line == "vars":
            for variable in self.variables:
                print(variable, "=", self.variables[variable])
            return 1

        # Show options  . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line == "options":
            for option in self.options:
                print(option, ":", self.options[option])
            return 1

        # Clear variables . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line == "clear":
            self.variables = {}
            return 1

        # Update options . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line.split(" ")[0] in self.options:
            if line.split(" ")[0] in ["implicit_multiplication", "tau_kills_pi", "always_sub", "always_num"]:
                if len(line.split(" ")) == 1:
                    self.options[line.split(" ")[0]] = True
                    return 1
                try:
                    val = line.split(" ")[1].lower() in ['on', 'true', '1']
                    self.options[line.split(" ")[0]] = val
                except IndexError:
                    return self.perr(f"Error updating option "
                         f"{line.split(' ')[0]}. Please follow the syntax "
                         f":\n"
                         f"symi> {line.split(' ')[0]} on|off")
                return 1
            elif line.split(" ")[0] in ["num_tolerance"]:
                try:
                    val = eval(line.split(" ")[1])
                    self.options[line.split(" ")[0]] = val
                except (IndexError, NameError):
                    return self.perr(f"Error updating option "
                         f"{line.split(' ')[0]}. Please follow the syntax "
                         f":\n"
                         f"symi> {line.split(' ')[0]} value")
                return 1
            else:
                try:
                    val = line.split(" ")[1]
                    self.options[line.split(" ")[0]] = val
                except (IndexError, NameError):
                    return self.perr(f"Error updating option "
                         f"{line.split(' ')[0]}. Please follow the syntax "
                         f":\n"
                         f"symi> {line.split(' ')[0]} value")
                return 1

        # Import  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line.split(" ")[0] == "import":
            try:
                if line.split(" ")[1].lower() == 'physics_constants':
                    self.variables = {**self.variables, **libs.physics_constants}
                else:
                    return self.perr(f"Error importing package "
                         f"{line.split(' ')[0]}. Please use a valid "
                         f"package "
                         f"name")
            except IndexError:
                return self.perr(f"Syntax error. "
                     f"{line.split(' ')[0]}. Please follow the syntax :\n"
                     f"symi> import package")
            return 1

        # Exit  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line.strip().lower() == "exit":
            self.exit()
            return 0

        # Substitution  . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line[-2:] == "!!":
            self.num = True
            line = line[:-1]
        else:
            self.num = self.options["always_num"]
        if line[-1] == "!":
            self.sub = True
            line = line[:-1]
        else:
            self.sub = self.options["always_sub"]

        # Limit . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if line[:3] == "lim" and "?" in line and "->" in line:
            limvar = self.expr2sympy(line[3:].split("->")[0])
            limvalstr = line[3:].split("->")[1].split("?")[0].strip()
            direction = '+'
            if limvalstr.endswith('-'):
                direction = '-'
                limvalstr = limvalstr[:-1]
            elif limvalstr.endswith('+'):
                limvalstr = limvalstr[:-1]
            limvalue = self.expr2sympy(limvalstr)

            fct = self.expr2sympy(line.split("?")[1])
            oldlimvar = limvar
            sub_sym = Symbol("__SUB__SYMBOL__LIMIT__")
            if type(limvar) != type(sub_sym):
                fct = fct.subs(limvar, sub_sym)
                limvar = sub_sym

            lim = simplify(
                limit(fct, limvar, limvalue, dir=direction).subs(sub_sym, oldlimvar))
            self.print(lim)
            self.variables["ans_"] = lim
            return 1

        # Solve Equation  . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if '?' in line:
            eqns_list, vars_list = line.split("?")
            eqns = eqns_list.split(";")
            varss = vars_list.strip().split(';')
            tru_eqns = []
            for eqn in eqns:
                left, right = eqn.split("=")
                if right.strip() in ['inf', 'oo', '-inf', '-oo']:
                    sign = '-' if '-' in right.strip() else ""
                    tru_eqns.append(self.expr2sympy(f"{sign}1/({left})"))
                elif left.strip() in ['inf', 'oo', '-inf', '-oo']:
                    sign = '-' if '-' in left.strip() else ""
                    tru_eqns.append(self.expr2sympy(f"{sign}1/({right})"))
                else:
                    lft = self.expr2sympy(left)
                    rht = self.expr2sympy(right)
                    tru_eqns.append(lft - rht)

            tru_vars = [self.expr2sympy(x) for x in varss if x.strip() != '']
            sol = solve(tru_eqns, tru_vars)
            if isinstance(sol, dict):
                for s in sol:
                    self.variables[str(s)] = sol[s]
            sol = self.sub_num(sol)
            self.print(sol)
            return 1

        # Affectation . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        if "=" in line:
            var_name = self.expr2sympy(line.split("=")[0])
            var_val = self.expr2sympy(line.split("=")[1])

            self.variables[str(var_name)] = self.sub_num(var_val)
            self.update_completer()
            return 1

        # Show Result . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

        else:
            simplified = self.sub_num(self.expr2sympy(line))
            for var in self.variables:
                if simplified - self.expr2sympy(var) == 0:
                    self.print(self.sub_num(self.variables[var]))
                    return 1
            self.print(simplified)
            self.variables["ans_"] = simplified
            return 1
