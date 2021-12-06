import pre_definition.params as params
import pre_definition.stdio as stdio
import pytest
import re
import sys
from io import StringIO


def test_stdio_stdout_sb():
    curr = sys.stdout
    sb = StringIO()
    with stdio.stdio(output=sb):
        print(1, 2, 3)
    assert sb.getvalue() == '1 2 3\n'
    assert sys.stdout is curr


def test_stdio_stdout_bool():
    curr = sys.stdout
    with stdio.stdio(output=True) as cm:
        print(1, 2, 3)
    assert cm.output_get() == '1 2 3\n'
    assert sys.stdout is curr


def test_stdio_stdout_reenter():
    curr = sys.stdout
    sb = StringIO()
    with stdio.stdio(output=sb):
        print(1, 2, 3)
        with stdio.stdio(output=True) as cm:
            print(4, 5, 6)
        assert sys.stdout is sb
        print(7, 8, 9)
    assert sys.stdout is curr
    assert cm.output_get() == '4 5 6\n'
    assert sb.getvalue() == '1 2 3\n7 8 9\n'


def test_stdio_stdout_exception_recover():
    class StdioException(Exception):
        pass

    curr = sys.stdout
    try:
        with stdio.stdio(output=True):
            raise StdioException()
    except StdioException:
        assert sys.stdout is curr


def test_stdio_stderr_sb():
    curr = sys.stderr
    sb = StringIO()
    with stdio.stdio(error=sb):
        print(1, 2, 3, file=sys.stderr)
    assert sb.getvalue() == '1 2 3\n'
    assert sys.stderr is curr


def test_stdio_stderr_bool():
    curr = sys.stderr
    with stdio.stdio(error=True) as cm:
        print(1, 2, 3, file=sys.stderr)
    assert cm.error_get() == '1 2 3\n'
    assert sys.stderr is curr


def test_stdio_stderr_reenter():
    curr = sys.stderr
    sb = StringIO()
    with stdio.stdio(error=sb):
        print(1, 2, 3, file=sys.stderr)
        with stdio.stdio(error=True) as cm:
            print(4, 5, 6, file=sys.stderr)
        assert sys.stderr is sb
        print(7, 8, 9, file=sys.stderr)
    assert sys.stderr is curr
    assert cm.error_get() == '4 5 6\n'
    assert sb.getvalue() == '1 2 3\n7 8 9\n'


def test_stdio_stderr_exception_recover():
    class StdioException(Exception):
        pass

    curr = sys.stderr
    try:
        with stdio.stdio(error=True):
            raise StdioException()
    except StdioException:
        assert sys.stderr is curr


def test_stdio_stdin_sb():
    curr = sys.stdin
    sb = StringIO('1 2 3\n')
    with stdio.stdio(input=sb):
        a, b, c = map(int, input().split())
    assert (a, b, c) == (1, 2, 3)
    assert sys.stdin is curr


def test_stdio_stdin_bool():
    curr = sys.stdin
    with stdio.stdio(input=True) as cm:
        cm.input_write('1 2 3\n')
        a, b, c = map(int, input().split())
    assert (a, b, c) == (1, 2, 3)
    assert sys.stdin is curr


def test_stdio_stdin_buffered():
    curr = sys.stdin
    with stdio.stdio(input=True) as cm:
        cm.input_write('1 2 3\n4 5 6\n')
        a = list(map(int, input().split()))
        cm.input_write('7 8 9\n')
        b = list(map(int, input().split()))
        c = list(map(int, input().split()))
    assert (a, b, c) == ([1, 2, 3], [4, 5, 6], [7, 8, 9])
    assert sys.stdin is curr


def test_stdio_stdin_string():
    curr = sys.stdin
    with stdio.stdio(input='1 2 3') as cm:
        a, b, c = map(int, input().split())
    assert (a, b, c) == (1, 2, 3)
    assert sys.stdin is curr


def test_stdio_stdin_reenter():
    curr = sys.stdin
    sb = StringIO('1 2 3\n4 5 6')
    with stdio.stdio(input=sb):
        a = list(map(int, input().split()))
        with stdio.stdio(input='7 8 9') as cm:
            b = list(map(int, input().split()))
        assert sys.stdin is sb
        c = list(map(int, input().split()))
    assert sys.stdin is curr
    assert (a, b, c) == ([1, 2, 3], [7, 8, 9], [4, 5, 6])


def test_stdio_stdin_exception_recover():
    class StdioException(Exception):
        pass

    curr = sys.stdin
    try:
        with stdio.stdio(input=True):
            raise StdioException()
    except StdioException:
        assert sys.stdin is curr


def test_merge_dicts():
    d1 = {1: 2}
    d2 = {2: 3}
    r = {1: 2, 2: 3}
    assert params.merge_dicts([d1, d2]) == r


def test_collapse_dicts_collection_into_params():
    d1 = {1: 2}
    d2 = {2: 3}
    d3 = {3: 4}
    r1 = {1: 2, 2: 3}
    r2 = {2: 3, 3: 4}
    assert list(params.collapse_dicts_collection_into_params([[d1, d2], [d2, d3]])) == [r1, r2]


def test_dict_gen_1():
    names = ['a']
    values = [1, 2, 3]
    r = [{'a': 1}, {'a': 2}, {'a': 3}]
    assert list(params.dict_gen(names, values)) == r


def test_dict_gen_many():
    names = ['a', 'b']
    values = [(1, 2), (2, 3), (3, 4)]
    r = [{'a': 1, 'b': 2}, {'a': 2, 'b': 3}, {'a': 3, 'b': 4}]
    assert list(params.dict_gen(names, values)) == r


def test_convert_params_assert_tuples():
    m = '`params[1]` should be an array of 2-sized tuples!'

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), 'b', [2], ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b1', 'b2', [2]), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b',), ('c', [3])])


def test_convert_params_assert_comma_separated():
    m = 'First part of tuple in `params[1]` should be a comma separated string of identifiers!'

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('!@#$', [2]), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), (',b', [2]), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b,', [2]), ('c', [3])])


def test_convert_params_assert_iterable():
    m = 'Second part of tuple in `params[1]` should be iterable!'

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b', 1), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b', 'text'), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b', None), ('c', [3])])


def test_convert_params_assert_tuple_size():
    m = 'Second part of tuple in `params[1]` should be a collection of tuples size 2!'

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b,d', [(1,)]), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b,d', [(1, 2), (3,)]), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b,d', [1, 2, 3]), ('c', [3])])

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b,d', ['xx', 'yy']), ('c', [3])])


def test_convert_params_assert_same_names():
    m = 'Same param names at 0 and 2 indexes of `params`!'

    with pytest.raises(AssertionError, match=re.escape(m)):
        params.convert_params([('a', [1]), ('b', [2]), ('a,c', [(3, 4)])])


def assert_have_same_items(xs, ys):
    for x in xs:
        assert x in ys
    for y in ys:
        assert y in xs


def test_convert_params():
    a = ('a', range(3))
    bc = ('b,c', [(1, 2), (3, 4)])
    d = ('d', ['x'])
    r = [{'a': 0, 'b': 1, 'c': 2, 'd': 'x'},
         {'a': 0, 'b': 3, 'c': 4, 'd': 'x'},
         {'a': 1, 'b': 1, 'c': 2, 'd': 'x'},
         {'a': 1, 'b': 3, 'c': 4, 'd': 'x'},
         {'a': 2, 'b': 1, 'c': 2, 'd': 'x'},
         {'a': 2, 'b': 3, 'c': 4, 'd': 'x'},
         ]

    assert_have_same_items(list(params.convert_params([a, bc, d])), r)


def test_call_printer():
    def foo(a, b, c):
        print(a, b, c)

    r = params.call_printer(foo, dict(a=1, b=2, c=3))
    assert r == '1 2 3\n'


def test_call_printer_with_side_effect():
    side_effect = StringIO()

    def foo(a, b, c):
        print('side effect', file=side_effect)
        print(a, b, c)

    r = params.call_printer(foo, dict(a=1, b=2, c=3))
    assert r == '1 2 3\n'
    assert side_effect.getvalue() == 'side effect\n'


def test_call_printer_assert():
    def foo():
        assert False

    current_stdout = sys.stdout

    with pytest.raises(AssertionError):
        params.call_printer(foo)

    assert sys.stdout == current_stdout


def strendl(x):
    if isinstance(x, str):
        return x
    return f'{x}\n'


def to_strendl(xs):
    return list(map(strendl, xs))


def test_gen_all():
    ps = [{'a': 1, 'b': 2}, {'a': 2, 'b': 3}, {'a': 3, 'b': 4}, {'a': 4, 'b': 5}, {'a': 5, 'b': 6}]
    r = to_strendl([2, 6, 12, 20, 30])
    assert list(params.gen_all(ps)(lambda a, b: print(a * b))()) == r


def test_gen_n():
    ps = [{'a': 1, 'b': 2}, {'a': 2, 'b': 3}, {'a': 3, 'b': 4}, {'a': 4, 'b': 5}, {'a': 5, 'b': 6}]
    r = to_strendl([2, 6, 12])
    assert list(params.gen_n(ps, n=3)(lambda a, b: print(a * b))()) == r


def test_gen_sample():
    _6 = {'a': 2, 'b': 3}
    _12 = {'a': 3, 'b': 4}

    ps = [{'a': 1, 'b': 2}, _6, _12, {'a': 4, 'b': 5}, {'a': 5, 'b': 6}]
    r = to_strendl([20, 6, 12])
    assert list(params.gen_sample(ps, sample=0.6)(lambda a, b: print(a * b))()) == r

    ps = [{'a': 1, 'b': 2}, _12, _6, {'a': 4, 'b': 5}, {'a': 5, 'b': 6}]
    r = to_strendl([20, 12, 6])
    assert list(params.gen_sample(ps, sample=0.6)(lambda a, b: print(a * b))()) == r


def test_params_not_allowed():
    ps = [('a', [1]), ('b', [2]), ('c,d', [(3, 4)])]

    bi_s = 'Not allowed combination of n=0(BAD INTEGER) and sample=<object SENTINEL>(SENTINEL)!'
    with pytest.raises(AssertionError, match=re.escape(bi_s)):
        params.params(ps, n=0)

    bi_s = 'Not allowed combination of n=-7(BAD INTEGER) and sample=<object SENTINEL>(SENTINEL)!'
    with pytest.raises(AssertionError, match=re.escape(bi_s)):
        params.params(ps, n=-7)

    s_bi = 'Not allowed combination of n=<object SENTINEL>(SENTINEL) and sample=2(BAD INTEGER)!'
    with pytest.raises(AssertionError, match=re.escape(s_bi)):
        params.params(ps, sample=2)

    s_bi = 'Not allowed combination of n=<object SENTINEL>(SENTINEL) and sample=-1(BAD INTEGER)!'
    with pytest.raises(AssertionError, match=re.escape(s_bi)):
        params.params(ps, sample=-1)

    s_bf = 'Not allowed combination of n=<object SENTINEL>(SENTINEL) and sample=1.1(BAD FLOAT)!'
    with pytest.raises(AssertionError, match=re.escape(s_bf)):
        params.params(ps, sample=1.1)

    s_bf = 'Not allowed combination of n=<object SENTINEL>(SENTINEL) and sample=-0.1(BAD FLOAT)!'
    with pytest.raises(AssertionError, match=re.escape(s_bf)):
        params.params(ps, sample=-0.1)

    gg = 'Not allowed combination of n=10(positive int) and sample=0.5(proportion)!'
    with pytest.raises(AssertionError, match=re.escape(gg)):
        params.params(ps, n=10, sample=0.5)


def test_params_gen_all():
    ps = [('a,b', [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)])]
    r = to_strendl([2, 6, 12, 20, 30])
    assert list(params.params(ps)(lambda a, b: print(a * b))()) == r


def test_params_gen_n():
    ps = [('a,b', [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)])]
    r = to_strendl([2, 6, 12])
    assert list(params.params(ps, n=3)(lambda a, b: print(a * b))()) == r


def test_params_gen_sample():
    _6 = (2, 3)
    _12 = (3, 4)

    ps = [('a,b', [(1, 2), _6, _12, (4, 5), (5, 6)])]
    r = to_strendl([20, 6, 12])
    assert list(params.params(ps, sample=0.6)(lambda a, b: print(a * b))()) == r

    ps = [('a,b', [(1, 2), _12, _6, (4, 5), (5, 6)])]
    r = to_strendl([20, 12, 6])
    assert list(params.params(ps, sample=0.6)(lambda a, b: print(a * b))()) == r


def test_params_is_dataset():
    ps = [('a,b', [(1, 2)])]
    f = params.params(ps)(lambda a, b: a * b)
    assert hasattr(f, 'is_dataset')
