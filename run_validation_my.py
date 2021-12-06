import logging as log

from extra.introspection import collect_datasets
from pre_definition.solve_caller import call_solve
from pre_definition.stdio import stdio
from implementation.solver import solver, input_reader
from my import generate, check, solve


def main():
    log.info('check datasets')
    datasets = collect_datasets()
    dss = []
    for _, f in datasets:
        dss += list(f())

    gdss = generate()
    assert dss == list(map(lambda x: x[0], gdss)), 'Produced different datasets!'

    log.info('checker validation')
    for ds, clue in gdss:
        with stdio(input=ds):
            input_data = input_reader()
        with stdio(output=True) as cm:
            call_solve(solver, input_data)
        reply = solve(ds)
        assert reply == cm.output_get(), 'Produced different solutions!'

        res = check(reply, clue)
        if isinstance(res, bool):
            assert res, 'Failed check correct solution'
        else:
            assert res[0], f'Failed check correct solution cause "{res[1]}"'


if __name__ == '__main__':
    log.basicConfig(level=log.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    main()
