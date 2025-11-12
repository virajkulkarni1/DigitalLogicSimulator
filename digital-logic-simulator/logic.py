"""Logic gate functions for Boolean operations."""

def AND(a, b):
    """Returns True if both inputs are True, False otherwise."""
    return a and b

def OR(a, b):
    """Returns True if at least one input is True, False otherwise."""
    return a or b

def NOT(a):
    """Returns True if input is False, False if input is True."""
    return not a

def NAND(a, b):
    """Returns False if both inputs are True, True otherwise."""
    return not (a and b)

def NOR(a, b):
    """Returns True if both inputs are False, False otherwise."""
    return not (a or b)

def XOR(a, b):
    """Returns True if inputs are different, False if they are the same."""
    return a != b


