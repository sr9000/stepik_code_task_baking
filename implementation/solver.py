def input_reader():
    h, w = map(int, input().split())
    table = [input().split() for _ in range(h)]
    return h, w, table


def hinter(h, w, table):
    return h + w - 1


def solver(h, w, table):
    for k in range(h):
        i, j = k, 0
        s = ''
        while i >= 0 and j < w:
            s += table[i][j]
            i -= 1
            j += 1
        print('_' * (h - k - 1) + ' '.join(s))
    for k in range(1, w):
        i, j = h - 1, k
        s = ''
        while i >= 0 and j < w:
            s += table[i][j]
            i -= 1
            j += 1
        print('_' * k + ' '.join(s))
