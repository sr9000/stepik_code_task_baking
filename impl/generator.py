from impl.private._params import params, ds2str
from impl.private._tag import dataset

XXX, (YYY, ZZZ) = 1, (2,3)

@dataset
def particular():
    return [
        ds2str([[1, 1]]),
        ds2str([[-100, -100]]),
        ds2str([[100, -90]]),
        ds2str([[12, 13]]),
        ds2str([[10 ** 5, 23 ** 4]]),
    ]


@params([
    ('s', [1, 3, 9]),
    ('d', [3, 5, 7, 9, 11])
])
def sumdiff_odd(s, d):
    assert (s + d) % 2 == 0
    a = (s + d) // 2
    b = s - a
    print(a, b)


@params([
    ('s', [2, 4, 10]),
    ('d', [4, 6, 8, 10, 12])
])
def sumdiff_even(s, d):
    assert (s + d) % 2 == 0
    a = (s + d) // 2
    b = s - a
    print(a, b)
