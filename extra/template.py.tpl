from pre_definition.stdio import stdio
from pre_definition.solve_caller import call_solve
from implementation.solver import input_reader, solver
from implementation.checker import output_reader, checker


def generator():
    for f in DATASETS_FUNCTIONS:
        for ds in f():
            with stdio(input=ds):
                input_data = input_reader()
            with stdio(output=True) as cm:
                call_solve(solver, input_data)
            yield ds, (ds, cm.output_get())


def generate():
    return list(generator())


def check(reply, clue):
    try:
        instr, expstr = clue
        with stdio(input=instr):
            input_data = input_reader()
        with stdio(input=expstr):
            expected_data = output_reader()
        with stdio(input=reply):
            result_data = output_reader()

        checker(input_data, expected_data, result_data)
    except Exception as e:
        return False, str(e)
    else:
        return True


def solve(ds):
    with stdio(input=ds):
        input_data = input_reader()

    with stdio(output=True) as cm:
        call_solve(solver, input_data)

    return cm.output_get()
