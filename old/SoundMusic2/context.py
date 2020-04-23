# Context for the REPL, for usability.

_context = {}

def apply(args):
    global _context
    new_args = []
    for arg in args:
        if arg in _context and isinstance(_context[arg], str):
            new_args.append(_context[arg])
        else:
            new_args.append(arg)
    return new_args

def define(name, val):
    global _context
    _context[name] = val

def clear():
    global _context
    _context = {}