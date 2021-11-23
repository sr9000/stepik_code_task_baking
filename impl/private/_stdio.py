import sys
from contextlib import contextmanager
from io import StringIO, SEEK_END
from typing import ContextManager


class Std:
    def input_write(self, s: str):
        ...

    def output_get(self):
        ...

    def error_get(self):
        ...


class Blank:
    pass


@contextmanager
def stdio(input=None, output=None, error=None) -> ContextManager[Std]:
    current = sys.stdin, sys.stdout, sys.stderr

    cm = init_stdio_cm()

    mask_input(cm, input)
    mask_output(cm, output)
    mask_error(cm, error)

    try:
        yield cm
    finally:
        sys.stdin, sys.stdout, sys.stderr = current


def mask_error(cm, error):
    if error is not None:
        if isinstance(error, bool) and error:
            serr = StringIO()
            sys.stderr = serr
            cm.error_get = serr.getvalue
        else:
            sys.stderr = error


def mask_output(cm, output):
    if output is not None:
        if isinstance(output, bool) and output:
            sout = StringIO()
            sys.stdout = sout
            cm.output_get = sout.getvalue
        else:
            sys.stdout = output


def special_write(sb, s):
    pos = sb.tell()
    sb.seek(0, SEEK_END)
    sb.write(s)
    sb.seek(pos)


def mask_input(cm, input):
    if input is not None:
        if isinstance(input, bool) and input:
            sin = StringIO()
            sys.stdin = sin
            cm.input_write = lambda s: special_write(sin, s)
        elif isinstance(input, str):
            sin = StringIO(input)
            sys.stdin = sin
            cm.input_write = lambda s: special_write(sin, s)
        else:
            sys.stdin = input


def init_stdio_cm():
    cm = Blank()
    cm.input_write = lambda s: NotImplemented
    cm.output_get = lambda: NotImplemented
    cm.error_get = lambda: NotImplemented
    return cm
