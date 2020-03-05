import copy

_all_exceptions = []

def save_exception(e):
    global _all_exceptions
    _all_exceptions.append(e)

def clear_exceptions():
    global _all_exceptions
    _all_exceptions = []

def get_exceptions():
    global _all_exceptions
    return copy.deepcopy(_all_exceptions)

def n_exceptions():
    global _all_exceptions
    return len(_all_exceptions)
