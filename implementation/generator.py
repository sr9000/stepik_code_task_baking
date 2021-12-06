from random import Random

from pre_definition.params import ds2str, params
from pre_definition.tag import dataset


@dataset
def particular():
    return [
        ds2str([[1, 1],
                [1]
                ]),
        ds2str([[2, 2],
                [1, 2],
                [3, 4],
                ]),
    ]


@params([
    ('h', [1, 2, 3, 4, 5, 10, 11, 12, 20, 25, 33, 42, 66, 77, 89, 90, 100]),
    ('w', [1, 2, 3, 4, 5, 10, 11, 12, 20, 25, 33, 42, 66, 77, 89, 90, 100]),
], sample=0.05)
def bars(h, w):
    rng = Random()
    rng.seed(h + w + h * w)
    print(h, w)
    for _ in range(h):
        print(*rng.choices('0123456789', k=w))
