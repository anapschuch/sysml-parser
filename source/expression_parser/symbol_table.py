from asteval import make_symbol_table
from scipy.interpolate import interpn as scipy_interpolate


def interpn(points, values, xi):
    return scipy_interpolate(points, values, xi)


symbol_table = make_symbol_table(use_numpy=True, interpn=interpn)
