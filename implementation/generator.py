from random import Random

from pre_definition.params import ds2str, params
from pre_definition.tag import dataset


@params([
    ('n', range(1, 11)),
])
def small(n):
    print(n)


@params([
    ('n', range(100, 5000)),
], n=30)
def big(n):
    print(n)


@dataset
def huge():
    return [
        ds2str([[6666]]),
        ds2str([[8000]]),
        ds2str([[9000]]),
        ds2str([[10_000]]),
    ]
