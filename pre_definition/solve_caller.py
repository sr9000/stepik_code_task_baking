from collections.abc import Iterable as ABCIterable


def call_with_args(func, args):
    if isinstance(args, dict):
        return func(**args)
    elif isinstance(args, ABCIterable):
        return func(*args)
    else:
        return func(args)
