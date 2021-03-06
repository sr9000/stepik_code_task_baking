import logging as log
import sys
from pathlib import Path

from implementation.checker import output_reader, checker as check
from implementation.solver import input_reader, solver as solve, hinter as get_hint
from pre_definition.solve_caller import call_with_args
from pre_definition.stdio import stdio


def main():
    log.basicConfig(level=log.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    log.info(f'--- Started: {sys.argv[0]} ---')

    ins, outs = collect_samples()

    pairs = match_samples(ins, outs)

    has_failed = False
    for name, (fin, fout) in pairs.items():
        try:
            check_sample(fin, fout)
            log.debug(f'Sample "{name}": PASSED')
        except Exception as e:
            has_failed = True
            log.error(f'Failed to check sample "{name}"', exc_info=False)
            cause = e
            while cause:
                log.error(str(cause), exc_info=False)
                cause = cause.__cause__

    if not has_failed:
        log.info('All samples are passed')
    else:
        quit(-1)


def check_sample(fin: Path, fout: Path):
    # read input
    with stdio(input=fin.open()):
        try:
            input = input_reader()
        except Exception as e:
            raise Exception(f'Cannot read "{fin.name}"') from e

    # get hint
    try:
        hint = call_with_args(get_hint, input)
    except Exception as e:
        raise Exception(f'Cannot get hint for "{fin.name}"') from e

    # read output
    with stdio(input=fout.open()):
        try:
            expected = call_with_args(output_reader, hint)
        except Exception as e:
            raise Exception(f'Cannot read "{fout.name}"') from e

    # run solution
    with stdio(output=True) as solution:
        try:
            call_with_args(solve, input)
        except Exception as e:
            raise Exception(f'Cannot solve "{input}"') from e

    # read solution output
    with stdio(input=solution.output_get()):
        try:
            answer = call_with_args(output_reader, hint)
        except Exception as e:
            raise Exception(f'Cannot read "{fout.name}"') from e

    # run checker
    check(input, expected, answer)


def match_samples(ins, outs):
    match = set(ins) & set(outs)
    pairs = {name: (ins[name], outs[name]) for name in match}
    total = len(set(ins) | set(outs))

    if len(pairs) != total:
        log.warning(f'Not all sample files match each other ({len(pairs)} / {total})')

    return pairs


def collect_samples():
    ins = dict()
    outs = dict()
    for f in Path('implementation/sample').iterdir():
        if not f.is_file():
            continue
        if f.match('*.in'):
            ins[f.stem] = f
        if f.match('*.out'):
            outs[f.stem] = f

    log.info(f'Input files: {len(ins)}')
    log.info(f'Output files: {len(outs)}')

    return ins, outs


if __name__ == '__main__':
    main()
