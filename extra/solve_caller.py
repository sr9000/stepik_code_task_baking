from collections.abc import Iterable as ABCIterable


def call_solve(solve, input):
    if isinstance(input, dict):
        solve(**input)
    elif isinstance(input, ABCIterable):
        solve(*input)
    else:
        solve(input)
