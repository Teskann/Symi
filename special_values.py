"""
This  file  contains all the special values supported by Symi expressions, and
how they are converted to SymPy functions.
"""

from sympy.parsing.sympy_parser import parse_expr
from sympy import laplace_transform, Symbol, simplify, Heaviside, DiracDelta


def get_values():
    """
    Get the special values as a dict where the keys are the Symi expressions
    ans the values are the corresponding SymPy values.

    Returns
    -------
    values : tuple of dict
        Correspondences between Symi and Sympy.

        Values[0] gives the basic function replacements,
        values[1] gives the operator replacements,
        values[2] gives the constants replacements
        values[3] gives the advances function replacements
    """
    fcts = {"arccos": "acos",
            "arcsin": "asin",
            "arctan": "atan",
            "conj": "conjugate",
            "abs": "Abs",
     }

    operators = {}

    constants = {"i": "I",
                 "j": "J",
                 "inf": "oo",
                 "e": "E"}

    advanced = {"Laplace": lambda __wild_sym__:
                laplace_transform(parse_expr(str(__wild_sym__)), parse_expr("t"),
                                  parse_expr("s"), noconds=True),
                "step": lambda __wild_sym__: Heaviside(__wild_sym__),
                "dirac": lambda __wild_sym__: DiracDelta(__wild_sym__),
                "sym": lambda __wild_sym__:
                Symbol(str(__wild_sym__))
                }
    advanced["L"] = advanced["Laplace"]

    return fcts, operators, constants, advanced