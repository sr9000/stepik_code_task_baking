def output_reader(hint):
    return [input() for _ in range(hint)]


def checker(input, expected, result):
    assert result == expected, 'Wrong!'
