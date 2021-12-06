import logging as log
from pathlib import Path

from extra.helper import clear_dir
from extra.introspection import collect_datasets
from implementation.solver import input_reader, solver as solve
from pre_definition.solve_caller import call_solve
from pre_definition.stdio import stdio


def main():
    log.basicConfig(level=log.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    datasets = collect_datasets()
    dsnowidth = len(str(len(datasets)))

    dsdir = Path('dataset')
    assert dsdir.exists() and dsdir.is_dir()

    clear_dir(dsdir)

    fulldir = dsdir / 'full'
    fulldir.mkdir(exist_ok=True)
    log.debug(f'Dir "{fulldir}" has been created')

    try:
        build_datasets(datasets, dsdir, dsnowidth, fulldir)
    except Exception:
        log.exception(f'Failed to build dataset')
        quit(-1)

    log.info(f'Dataset has been build')


def build_datasets(datasets, dsdir, dsnowidth, fulldir):
    fullno = 0
    for dsno, (name, ds) in enumerate(datasets, start=1):
        currdir = dsdir / f'{dsno:0{dsnowidth}}_{name}'
        currdir.mkdir(exist_ok=True)
        log.debug(f'Dir "{currdir}" has been created')

        for testno, data in enumerate(ds(), start=1):
            fullno += 1

            fulltest = fulldir / f'{fullno}.in'
            fulltest.write_text(data, encoding='utf-8')
            log.debug(f'Test file "{fulltest}" has been written')

            solve_file(fulltest)
            log.debug(f'Test file "{fulltest}" has been solved')

            currtest = currdir / f'{testno}.in'
            currtest.write_text(data, encoding='utf-8')
            log.debug(f'Test file "{currtest}" has been written')

            solve_file(currtest)
            log.debug(f'Test file "{currtest}" has been solved')


def solve_file(input_file: Path):
    with stdio(input=input_file.open()):
        input = input_reader()

    output_file = input_file.with_suffix('.out')

    with stdio(output=output_file.open('w')):
        call_solve(solve, input)


if __name__ == '__main__':
    main()
