"""
Type conversion functions for synchronizing between LandscapeSim and SyncroSim.

Everything exported from SyncroSim is a string, but many of the numbers need to be converted to
integers or floating point numbers. To do this, we have a forward (SyncroSim -> LandscapeSim) conversion,
and a reverse (LandscapeSim -> SyncroSim) conversion.
"""


# Forward conversions
def default_int(value):
    return int(value) if len(value) else -1


def default_float(value):
    return float(value) if len(value) else -1


def empty_or_yes_to_bool(value):
    return value == 'Yes'


def time_int(value):
    return int(value) if len(value) else None


# Reverse conversions
def default_num_to_empty_or_int(value):     # Can be used on integers and floats
    return value if value != -1 else ''


def bool_to_empty_or_yes(value):
    return 'Yes' if value else ''
