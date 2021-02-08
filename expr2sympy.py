from expr_manager import find_everything, replace_many, apply_to_leaves
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, \
    function_exponentiation, implicit_multiplication, \
    implicit_multiplication_application, split_symbols, implicit_application,\
    convert_xor
from special_values import get_values
from sympy import Wild, nsimplify
from sympy import Symbol, Add, Mul, Pow, Function, Integer, Float, sin
from itertools import permutations
from sympy import default_sort_key, topological_sort


def expr2sympy(expr, options, variables):
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
        }

    variables: dict
        Symi variables

    Returns
    -------
    Sympy Expression

    """

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
    new_fct.append(["__SUB__", True])
    expr = replace_many(expr, old_fct, new_fct)
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
    for const in constants:
        sym = sym.subs(parse_expr(const), parse_expr(constants[const]))

    advanced["__SUB__"] = lambda __wild_sym__: subs(__wild_sym__, variables)
    wild_sym = Wild("__wild_sym__")
    for adv in list(advanced)[::-1]:
        f = parse_expr(adv + "(__tmp_sym__)")
        f = f.subs("__tmp_sym__", wild_sym)
        sym = sym.replace(f, advanced[adv])

    sym = parse_expr(str(sym), evaluate=True,
                     transformations=transformations)

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
        if options["num_tolerance"] is not None:
            exp = nsimplify(exp, tolerance=options["num_tolerance"]).evalf()
        else:
            exp = nsimplify(exp).evalf()
    return exp
