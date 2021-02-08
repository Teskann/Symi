from expr_manager import find_everything, replace_many, replace_var
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, \
    function_exponentiation, implicit_multiplication,\
    implicit_multiplication_application
from special_values import get_values
from sympy import Wild
from itertools import permutations
from sympy import default_sort_key, topological_sort


def expr2sympy(expr):
    """
    Converts a string expression to a Sympy expression.

    Parameters
    ----------
    expr : str
        String containing a Symi expression

    Returns
    -------
    Sympy Expression

    """

    fcts, operators, constants, advanced = get_values()

    transformations = standard_transformations + (implicit_multiplication_application, )

    old_fct = []
    new_fct = []
    for fct in fcts:
        old_fct.append([fct, True])
        new_fct.append([fcts[fct], True])
    for op in operators:
        old_fct.append([op, False])
        new_fct.append([operators[op], False])

    expr = replace_many(expr, old_fct, new_fct)
    sym = parse_expr(expr, transformations=transformations)

    wild_sym = Wild("__wild_sym__")
    for adv in advanced:
        f = parse_expr(adv + "(__tmp_sym__)")
        f = f.subs("__tmp_sym__", wild_sym)
        sym = sym.replace(f, advanced[adv])

    for const in constants:
        sym = sym.subs(parse_expr(const), parse_expr(constants[const]))

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

    var_tuple = [(key, variables[key]) for key in variables]

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
