"""
This file contains the dictionaries connecting the GUI text to the OpenFOAM dictionary entries.

"""
grad_schemes = {"Gauss Linear":"Gauss linear","Gauss Linear (Cell Limited)":"cellLimited Gauss Linear 1",
                "Gauss Linear (Face Limited)":"faceLimited Gauss Linear 1","Gauss Linear (Cell MD Limited)":"cellMDLimited Gauss Linear 1",
                "Gauss Linear (Face MD Limited)":"faceMDLimited Gauss Linear 1",
               "Least Squares":"leastSquares"}

div_schemes = {"Gauss Linear":"Gauss linear","Gauss Upwind":"Gauss upwind","Gauss Linear Upwind":"Gauss linearUpwind",
               "Gauss Limited Linear":"Gauss limitedLinear 1",}
temporal_schemes = {"Euler":"Euler","Crank-Nicolson":"crankNicolson","Steady State":"steadyState"}

laplacian_schemes = {"corrected ":"Gauss linear limited corrected 1","limited 0.333":"Gauss linear limited corrected 0.333",
                     "limited 0.5":"Gauss linear limited corrected 0.5","uncorrected":"Gauss linear limited corrected 0",}



def value_to_key(dict,value):
    """
    This function returns the key of a dictionary given a value.

    Args:
        dict: Dictionary to search.
        value: Value to search for.

    Returns:
        key: Key of the value in the dictionary.

    """
    for key in dict:
        if dict[key] == value:
            return key
    return None

def key_to_value(dict,key):
    """
    This function returns the value of a dictionary given a key.

    Args:
        dict: Dictionary to search.
        key: Key to search for.

    Returns:
        value: Value of the key in the dictionary.

    """
    return dict[key]
