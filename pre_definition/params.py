from collections.abc import Iterable as ABCIterable, Mapping as ABCMapping
from itertools import product
from random import Random
from typing import List, Tuple, Iterable

from pre_definition.stdio import stdio
from pre_definition.tag import dataset


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


def lmap(f, xs):
    return list(map(f, xs))


def is_tuple_len_2(obj):
    return isinstance(obj, tuple) and len(obj) == 2


def parse_comma_sep_ids(s):
    return lmap(str.strip, s.split(','))


def is_comma_sep_ids(obj):
    if not isinstance(obj, str):
        return False

    return all(map(str.isidentifier, parse_comma_sep_ids(obj)))


def is_collection(obj):
    return isinstance(obj, ABCIterable) and not isinstance(obj, str)


def parse_params(params):
    """
    Extract list of names + collapse iterators into lists
    :param params: list of tuples (str, iter)
    :return: list of tuples (list[str], list)
    """

    return [(parse_comma_sep_ids(names), list(values)) for names, values in params]


def is_tuple_len_(n):
    def _inner(obj):
        return isinstance(obj, tuple) and len(obj) == n

    return _inner


def have_exact_(names):
    def _inner(mapping):
        return set(names) == set(mapping.keys())

    return _inner


def is_corresponding_names_to_lists(obj):
    names, ls = obj
    if len(names) == 1:
        return True

    n = len(names)
    for values in ls:
        if isinstance(values, tuple):
            if not is_tuple_len_(n)(values):
                return False
        elif isinstance(values, ABCMapping):
            if not have_exact_(names)(values):
                return False
        else:
            return False
    return True


def any2tuple(names):
    def _inner(values):
        if isinstance(values, tuple):
            return values
        elif isinstance(values, ABCMapping):
            return tuple(values[nm] for nm in names)
        else:
            assert False, 'Impossible type error at conversion iters into tuples!'

    return _inner


def eliminate_dicts(obj):
    names, ls = obj
    if len(names) == 1:
        return obj
    else:
        return names, lmap(any2tuple(names), ls)


def convert_params(params):
    check = lmap(is_tuple_len_2, params)
    if not all(check):
        index = check.index(False)
        msg = f'`params[{index}]` should be an array of 2-sized tuples!'
        assert False, msg

    names = [x[0] for x in params]
    check = lmap(is_comma_sep_ids, names)
    if not all(check):
        index = check.index(False)
        msg = f'First part of tuple in `params[{index}]` should be a comma separated string of identifiers!'
        assert False, msg

    collections = [x[1] for x in params]
    check = lmap(is_collection, collections)
    if not all(check):
        index = check.index(False)
        msg = f'Second part of tuple in `params[{index}]` should be iterable!'
        assert False, msg

    # parsing names and collapsing iterables
    params = parse_params(params)

    check = lmap(is_corresponding_names_to_lists, params)
    if not all(check):
        index = check.index(False)
        plen = len(params[index][0])
        msg = (f'Second part of tuple in `params[{index}]` should be a collection of tuples size {plen} '
               f'or dict with exact keys!')
        assert False, msg

    params = lmap(eliminate_dicts, params)

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


def gen_n(params, n, seed, **kwargs):
    shuffled_params = list(params)
    Random(seed).shuffle(shuffled_params)

    def _decor(f):
        def _new_func():
            for i, p in enumerate(shuffled_params):
                if i == n:
                    return
                yield call_printer(f, p)

        return _new_func

    return _decor


def gen_sample(params, sample, seed, **kwargs):
    listed_params = list(params)
    n = max(1, int(len(listed_params) * sample))
    return gen_n(listed_params, n, seed)


def params(params: List[Tuple[str, Iterable]], n=SENTINEL, sample=SENTINEL, seed=42):
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
        seed=seed,
    )

    return lambda f: dataset(fproto(f))
