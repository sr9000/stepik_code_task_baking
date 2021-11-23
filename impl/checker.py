def output_reader():
    return int(input())


def checker(input, expected, result):
    assert expected == result, 'Fail!'
