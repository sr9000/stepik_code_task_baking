import sys
from itertools import dropwhile


def output_reader():
    lines = [ln.rstrip('\n') for ln in sys.stdin if ln]
    lines.reverse()
    lines = list(dropwhile(lambda x: not x.strip(), lines))
    lines.reverse()

    return lines


def checker(input, expected, result):
    assert result == expected, 'Wrong!'
