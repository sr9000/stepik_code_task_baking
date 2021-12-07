from itertools import product


def input_reader():
    return int(input())


def hinter(*args, **kwargs):
    pass


def solver(n):
    b, w = 1, 0
    for _ in range(n):
        b, w = w, b + w
    print(2 * b + w)

# def solver_slow(n):
#     template = [(0, 1)] * n
#     k = 0
#     for s in product(*template):
#         s = list(s)
#         if (s[0], s[-1]) != (0,0) and (0,0) not in zip(s[1:], s[:-1]):
#             k += 1
#     print(k)
