import logging as log

from extra.introspection import collect_datasets, collect_wrong_solutions
from implementation.checker import output_reader, checker as check
from implementation.solver import input_reader, solver as solve
from pre_definition.solve_caller import call_solve
from pre_definition.stdio import stdio


class ValidationException(Exception):
    pass


class AbsolutelyWrongException(ValidationException):
    pass


class PartiallyCorrectException(ValidationException):
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

    readed_stripped_sl = list(reading_solutions(solved_ds, stripping=True))
    log.info('stripped solutions is readable')

    # solutions passing check
    assert_solutions(readed_ds, readed_sl, readed_stripped_sl)
    log.info('solutions passing check')

    log.info('collect wrong solutions')
    wrsols = collect_wrong_solutions()

    # datasets is wrong_solvable
    wrsolved_ds = list(wrong_solving_datasets(readed_ds, wrsols))
    log.info('datasets is wrong_solvable')

    # wrong solutions is readable
    readed_wrsl = list(wrong_reading_solutions(wrsolved_ds))
    log.info('wrong solutions is readable')

    # wrong solutions fail at least one check (but also should pass at least one)
    assert_wrong_solutions(readed_ds, readed_sl, readed_wrsl)
    log.info('wrong solutions give representative feedback')


def assert_wrong_solutions(readed_ds, readed_sl, readed_wrsl):
    for wrname, wrans in readed_wrsl:
        try:
            assert_solutions(readed_ds, readed_sl, wrans)
        except PartiallyCorrectException:
            # expect exception from checking
            pass
        except AbsolutelyWrongException:
            # shit, this wrong solution is absolute garbage
            raise ValidationException(f'Wrong solution "{wrname}" did not pass any test, but should.')
        except Exception as e:
            # something goes wrong
            raise ValidationException(f'Wrong solution "{wrname}" goes bad with check.') from e
        else:
            # shit, we didnt catch wrong solution
            raise ValidationException(f'Wrong solution "{wrname}" passed all tests, but should fail at least one.')


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

    correct = 0
    wrong = 0
    first_error = None
    first_full_name = ''

    for (full_name1, indata), (full_name2, outdata), (full_name3, ansdata) in zip(readed_ds, readed_sl, answered_sl):
        assert full_name1 == full_name2, f'Checking solutions on different names'
        assert full_name1 == full_name3, f'Checking solutions on different names'
        try:
            check(indata, outdata, ansdata)
            correct += 1
        except Exception as e:
            wrong += 1
            if first_error is None:
                first_error = e
                first_full_name = full_name1

    if not correct:
        raise AbsolutelyWrongException(f'Failed to check solution {first_full_name}') from first_error
    elif wrong:
        raise PartiallyCorrectException(f'Failed to check solution {first_full_name}') from first_error


def reading_solutions(solved_ds, stripping=False):
    for full_name, sl in solved_ds:
        try:
            sl = sl.strip(' ') if stripping else sl
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
            r = cm.output_get()
            assert r == r.strip(' '), f'Solution of {full_name} did not pass stripping test'
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
        quit(-1)
