from colors import bcolors
from expr_manager import replace_many, apply_to_leaves, get_root_operation, \
    is_supported, pipe_to_func
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, \
    function_exponentiation, \
    implicit_multiplication_application, split_symbols, implicit_application,\
    convert_xor
from special_values import get_values
from sympy import Wild, nsimplify, integrate, diff, gamma, factorial, simplify
from sympy import Symbol, Add, Mul, Pow, Function, Integer, Float


def expr2sympy(expr, options, variables, sub):
    """
    Converts a string expression to a Sympy expression.

    Parameters
    ----------
    expr : str
        String containing a Symi expression

    options : dict
        dict containing the options for parsing.
        Might contain :

        {"implicit_multiplication" : ,
         "num_tolerance": ,
         "tau_kills_pi":
        }

    variables: dict
        Symi variables

    sub : bool
        True if the substitution must be applied.

    Returns
    -------
    Sympy Expression

    """

    if not is_supported(expr):
        print(f"{bcolors.WARNING}WARNING : The result given by this expression might be incorrect.\n"
              "Try to retype the expression without implicit multiplication.\n"
              "This warning can happen if you wrote useless parentheses, in "
              f"which case, the result should be correct.{bcolors.ENDC}")

    if sub:
        expr = apply_to_leaves(expr, ["@u", False])

    fcts, operators, constants, advanced = get_values()

    transformations_ = [implicit_application, function_exponentiation,
                        convert_xor]
    add_trans = []
    if options["implicit_multiplication"]:
        add_trans += [implicit_multiplication_application, split_symbols]

    transformations = (standard_transformations +
                       tuple(transformations_+add_trans))
    trans_i = standard_transformations + tuple(transformations_)

    old_fct = []
    new_fct = []
    for fct in fcts:
        old_fct.append([fct, True])
        new_fct.append([fcts[fct], True])
    for op in operators:
        old_fct.append([op, False])
        new_fct.append([operators[op], False])

    old_fct.append(["@u", False])
    new_fct.append(["__SUB", True])
    old_fct.append(["$u", False])
    new_fct.append(["__integrate", True])
    old_fct.append(["'s", False])
    new_fct.append(["__diff", True])
    old_fct.append(["!s", False])
    new_fct.append(["factorial", True])
    expr = pipe_to_func(expr)
    expr = replace_many(expr, old_fct, new_fct)
    is_smp = is_simplified(expr)
    expr = apply_to_leaves(expr, ["MySymbol", True], True)
    sym = parse_expr(expr, evaluate=True, transformations=trans_i,
                     global_dict={"Symbol": Symbol,
                                  "Add": Add,
                                  "Mul": Mul,
                                  "Pow": Pow,
                                  "Function": Function,
                                  "Integer": Integer,
                                  "Float": Float,
                                  "MySymbol": advanced["sym"]})
    if options["tau_kills_pi"]:
        constants["itau"] = "I*tau"
    for const in constants:
        sym = sym.subs(parse_expr(const), parse_expr(constants[const]))
    if options["tau_kills_pi"]:
        sym = sym.subs(parse_expr("tau"), parse_expr("2*pi"))
    advanced["__diff"] = (lambda __wild_sym__:
                          diff(parse_expr(str(__wild_sym__), transformations=transformations), parse_expr(options["diff_variable"]))
                          if options["diff_variable"] is not None
                          else diff(parse_expr(str(__wild_sym__), transformations=transformations)))
    advanced["__integrate"] = (lambda __wild_sym__:
                               integrate(parse_expr(str(__wild_sym__), transformations=transformations), parse_expr(options["integration_variable"]))
                               if options["integration_variable"] is not None
                               else integrate(parse_expr(str(__wild_sym__), transformations=transformations)))

    advanced["__SUB"] = lambda __wild_sym__: subs(__wild_sym__, variables)
    wild_sym = Wild("__wild_sym__")
    for adv in list(advanced)[::-1]:
        f = parse_expr(adv + "(__tmp_sym__)")
        f = f.subs("__tmp_sym__", wild_sym)
        sym = sym.replace(f, advanced[adv])

    sym = parse_expr(str(sym), evaluate=True,
                     transformations=transformations)
    for const in constants:
        sym = sym.subs(parse_expr(const), parse_expr(constants[const]))

    if is_smp:
        return simplify(sym)
    else:
        return sym


def subs(exp, variables):
    """
    Substitutes all the variables in the expression
    Parameters
    ----------
    exp : Sympy Expression

    variables : dict
        Keys are the old expressions, value the new ones

    Returns
    -------
    sub_exp : Sympy Expression
        Expression substituted
    """

    var_tuple = [(parse_expr(key), variables[key]) for key in variables]

    def recursive_sub(expr, replace):
        for _ in range(0, len(replace) + 1):
            new_expr = expr.subs(replace)
            if new_expr == expr:
                return new_expr, True
            else:
                expr = new_expr
        return new_expr, False

    res, _ = recursive_sub(exp, var_tuple)

    if is_simplified(str(exp)):
        return simplify(res)
    else:
        return res


def sub_num(exp, options, variables, sub, num):
    """
    Applies the substitution and the numeric computation

    Parameters
    ----------
    exp : Sympy Expression

    options : dict
        Symi options

    variables : dict
        Symi variables

    sub : bool
        True if substitution must be done

    num : bool
        True if the numeric application must be done

    Returns
    -------

    sub_num_exp : Sympy Expression
        Updated expression
    """
    if sub:
        exp = subs(exp, variables)
    if num:
        if options["tau_kills_pi"]:
            exp = exp.subs(parse_expr("tau"), parse_expr("2*pi"))
        if options["num_tolerance"] is not None:
            exp = nsimplify(exp, tolerance=options["num_tolerance"]).evalf()
        else:
            exp = nsimplify(exp).evalf()
    return exp


def is_simplified(expr):
    """
    Returns true if the expression must be simplified before being printed.
    It must not be simplified for rewrite-functions

    Parameters
    ----------
    expr : str
        Mathematical expression

    Returns
    -------

    bool
        True if it must be simplified, False otherwise
    """

    rewrite_fcts = ["expand", "factor", "cse", "collect", "cancel", "apart",
                    "trigsimp", "expand_trig", "powsimp", "expand_power_exp",
                    "expand_power_base", "powdenest", "expand_log", "logcombine",
                    "rewrite", "expand_func", "hyperexpand", "combsimp", "gammasimp"]

    root = get_root_operation(expr)
    return not (root[1] and any([x == root[0] for x in rewrite_fcts]))
