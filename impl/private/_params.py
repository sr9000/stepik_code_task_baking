from collections.abc import Iterable as ABCIterable
from itertools import product
from random import Random
from typing import List, Tuple, Iterable

from impl.private._stdio import stdio
from impl.private._tag import dataset


def ds2str(ds):
    return '\n'.join(' '.join(map(str, x)) for x in ds) + '\n'


class Sentinel:
    def __str__(self):
        return '<object SENTINEL>'

    def __repr__(self):
        return '<object SENTINEL>'


SENTINEL = Sentinel()


def merge_dicts(dicts):
    r = dict()
    for d in dicts:
        r.update(d)
    return r


def collapse_dicts_collection_into_params(dicts_collection):
    for dicts in dicts_collection:
        yield merge_dicts(dicts)


def dict_gen(names, values):
    for v in values:
        if len(names) == 1:
            yield {names[0]: v}
        else:
            yield dict(zip(names, v))


def convert_params(params):
    check = list(map(lambda x: isinstance(x, tuple) and len(x) == 2, params))
    if not all(check):
        index = check.index(False)
        msg = f'`params[{index}]` should be an array of 2-sized tuples!'
        assert False, msg

    check = list(map(lambda x: isinstance(x[0], str) and all(map(str.isidentifier, x[0].split(','))), params))
    if not all(check):
        index = check.index(False)
        msg = f'First part of tuple in `params[{index}]` should be a comma separated string of identifiers!'
        assert False, msg

    check = list(map(lambda x: isinstance(x[1], ABCIterable) and not isinstance(x[1], str), params))
    if not all(check):
        index = check.index(False)
        msg = f'Second part of tuple in `params[{index}]` should be iterable!'
        assert False, msg

    # convert iterables into lists
    params = [(names.split(','), list(values)) for names, values in params]

    check = list(map(lambda x: len(x[0]) == 1 or all(map(lambda y: isinstance(y, tuple) and len(x[0]) == len(y),
                                                         x[1])),
                     params))
    if not all(check):
        index = check.index(False)
        plen = len(params[index][0])
        msg = f'Second part of tuple in `params[{index}]` should be a collection of tuples size {plen}!'
        assert False, msg

    names = sorted([(name, i) for i, x in enumerate(params) for name in x[0]])
    unique_names = sorted(list(set([name for name, _ in names])))
    if len(names) != len(unique_names):
        msg = ''
        for nm1, nm2 in zip(names[:-1], names[1:]):
            if nm1[0] == nm2[0]:
                msg = f'Same param names at {nm1[1]} and {nm2[1]} indexes of `params`!'
                break
        assert False, msg

    # convert names and lists into dict generators
    dictgens = [dict_gen(names, values) for names, values in params]
    return collapse_dicts_collection_into_params(product(*dictgens))


def call_printer(f, ps=SENTINEL):
    if ps is SENTINEL:
        ps = {}

    with stdio(output=True) as std:
        f(**ps)

    return std.output_get()


def gen_all(params, **kwargs):
    def _decor(f):
        def _new_func():
            for p in params:
                yield call_printer(f, p)

        return _new_func

    return _decor


def gen_n(params, n, **kwargs):
    def _decor(f):
        def _new_func():
            for i, p in enumerate(params):
                if i == n:
                    return
                yield call_printer(f, p)

        return _new_func

    return _decor


def gen_sample(params, sample, **kwargs):
    params = list(params)
    Random(42).shuffle(params)
    n = max(1, int(len(params) * sample))
    return gen_n(params, n)


def params(params: List[Tuple[str, Iterable]], n=SENTINEL, sample=SENTINEL):
    n_category = None
    if n is SENTINEL:
        n_category = 'SENTINEL'
    if isinstance(n, int):
        if n > 0:
            n_category = 'positive int'
        else:
            n_category = 'BAD INTEGER'

    sample_category = None
    if sample is SENTINEL:
        sample_category = 'SENTINEL'
    if isinstance(sample, int):
        if sample == 1:
            sample = 1.0
        elif sample == 0:
            sample = 0.0
        else:
            sample_category = 'BAD INTEGER'
    if isinstance(sample, float):
        if 0.0 <= sample <= 1.0:
            sample_category = 'proportion'
        else:
            sample_category = 'BAD FLOAT'

    allowed_categories = {
        ('SENTINEL', 'SENTINEL'): gen_all,
        ('positive int', 'SENTINEL'): gen_n,
        ('SENTINEL', 'proportion'): gen_sample,
    }

    msg = f'Not allowed combination of n={n}({n_category}) and sample={sample}({sample_category})!'
    assert (n_category, sample_category) in allowed_categories, msg

    converted = convert_params(params)

    fproto = allowed_categories[(n_category, sample_category)](
        params=converted,
        n=n,
        sample=sample,
    )

    return lambda f: dataset(fproto(f))
