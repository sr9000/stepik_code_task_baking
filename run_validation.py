import logging as log

from extra.introspection import collect_datasets, collect_wrong_solutions
from extra.solve_caller import call_solve
from impl.checker import output_reader, checker as check
from impl.private._stdio import stdio
from impl.solver import input_reader, solver as solve


class ValidationException(Exception):
    pass


def main():
    log.info('collect_datasets')
    datasets = collect_datasets()

    # datasets is readable
    readed_ds = list(reading_datasets(datasets))
    log.info('datasets is readable')

    # datasets is solvable
    solved_ds = list(solving_datasets(readed_ds))
    log.info('datasets is solvable')

    # solutions is readable
    readed_sl = list(reading_solutions(solved_ds))
    log.info('solutions is readable')

    # solutions passing check
    assert_solutions(readed_ds, readed_sl)
    log.info('solutions passing check')

    log.info('collect wrong solutions')
    wrsols = collect_wrong_solutions()

    # datasets is wrong_solvable
    wrsolved_ds = list(wrong_solving_datasets(readed_ds, wrsols))
    log.info('datasets is wrong_solvable')

    # wrong solutions is readable
    readed_wrsl = list(wrong_reading_solutions(wrsolved_ds))
    log.info('wrong solutions is readable')

    # wrong solutions fail at least one check
    assert_wrong_solutions(readed_ds, readed_sl, readed_wrsl)
    log.info('wrong solutions fail at least one check')


def assert_wrong_solutions(readed_ds, readed_sl, readed_wrsl):
    for wrname, wrans in readed_wrsl:
        try:
            assert_solutions(readed_ds, readed_sl, wrans)
        except Exception:
            # expect exception from checking
            pass
        else:
            # shit, we didnt catch wrong solution
            raise ValidationException(f'Wrong solution "{wrname}" passes all tests')


def wrong_reading_solutions(wrsolved_ds):
    for wrname, wrsols in wrsolved_ds:
        try:
            yield wrname, list(reading_solutions(wrsols))
        except Exception as e:
            raise ValidationException(f'Failed to read wrong solution "{wrname}"') from e


def wrong_solving_datasets(readed_ds, wrsols):
    for wrname, wrcall in wrsols:
        try:
            yield wrname, list(solving_datasets(readed_ds, wrcall))
        except Exception as e:
            raise ValidationException(f'Failed to run wrong solution "{wrname}"') from e


def assert_solutions(readed_ds, readed_sl, answered_sl=None):
    if answered_sl is None:
        answered_sl = readed_sl

    for (full_name1, indata), (full_name2, outdata), (full_name3, ansdata) in zip(readed_ds, readed_sl, answered_sl):
        assert full_name1 == full_name2, f'Checking solutions on different names'
        assert full_name1 == full_name3, f'Checking solutions on different names'
        try:
            check(indata, outdata, ansdata)
        except Exception as e:
            raise ValidationException(f'Failed to check solution {full_name1}') from e


def reading_solutions(solved_ds):
    for full_name, sl in solved_ds:
        try:
            with stdio(input=sl):
                output_data = output_reader()
            yield full_name, output_data
        except Exception as e:
            raise ValidationException(f'Failed to read solution {full_name}') from e


def solving_datasets(readed_ds, solve_func=solve):
    for full_name, ds_data in readed_ds:
        try:
            with stdio(output=True) as cm:
                call_solve(solve_func, ds_data)
            yield full_name, cm.output_get()
        except Exception as e:
            raise ValidationException(f'Failed to solve dataset {full_name}') from e


def reading_datasets(datasets):
    for name, dsgen in datasets:
        for dsno, ds in enumerate(dsgen(), start=1):
            full_name = f'"{name}" #{dsno}'
            try:
                with stdio(input=ds):
                    input_data = input_reader()
                yield full_name, input_data
            except Exception as e:
                raise ValidationException(f'Failed to read dataset {full_name}') from e


if __name__ == '__main__':
    log.basicConfig(level=log.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

    try:
        main()
    except (ValidationException, AssertionError) as e:
        log.error(f'Failed to pass validation', exc_info=False)
        cause = e
        while cause:
            log.error(str(cause), exc_info=False)
            cause = cause.__cause__
