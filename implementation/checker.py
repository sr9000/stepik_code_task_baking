def output_reader(*args, **kwargs):
    return int(input())


def checker(input, expected, result):
    assert result == expected, 'Wrong!'
