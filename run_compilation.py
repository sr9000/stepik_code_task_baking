import ast
import logging as log
from importlib import import_module
from inspect import getfile, getmodule
from itertools import filterfalse
from pathlib import Path
from runpy import run_path
from typing import Type, Iterable

from astunparse import unparse

from extra.introspection import collect_datasets
from pre_definition.stdio import stdio

AST_IMPORTS = [ast.Import, ast.ImportFrom]
AST_NEW_NAMES = [ast.Assign, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef]


def is_any_samefile(target: Path, collection: Iterable[Path]):
    return any(target.samefile(f) for f in collection)


def factory_is_any_isinstance(collection: Iterable[Type]):
    def _internal(target):
        return any(isinstance(target, cls) for cls in collection)

    return _internal


def parse_module(modpath: Path, local_modules: Iterable[Path]):
    """
    Parsee module file, finds:
        - Non local Imports
        - Source Code
        - Local names
    :param modpath:
    :return: Non local Imports, Module Source Code, Local names
    """

    # read file
    content = modpath.read_text()

    # parse file
    ast_obj = ast.parse(content)

    nonlocal_imports = find_nonlocal_imports(ast_obj, local_modules)
    source_code = find_module_sourcecode(ast_obj)
    local_names = set(filter_local_names(modpath, ast_obj))

    return nonlocal_imports, source_code, local_names


def filter_local_names(modpath, ast_obj):
    namedefs = filter(factory_is_any_isinstance(AST_NEW_NAMES), ast_obj.body)
    ast_names = set(extract_names(namedefs))
    mdl_names = set(run_path(modpath))

    return ast_names.intersection(mdl_names)


def extract_names(namedefs):
    for df in namedefs:
        if isinstance(df, ast.ClassDef) or isinstance(df, ast.FunctionDef) or isinstance(df, ast.AsyncFunctionDef):
            yield df.name
        elif isinstance(df, ast.Assign):
            assert len(df.targets) == 1
            for nm in flatten_target(df.targets[0]):
                yield nm
        else:
            assert False, 'Impossible!'


def flatten_target(df):
    if isinstance(df, ast.Name):
        yield df.id
    elif isinstance(df, ast.Tuple):
        for tdf in df.elts:
            for nm in flatten_target(tdf):
                yield nm
    else:
        assert False, 'Impossible!'


def find_module_sourcecode(ast_obj):
    # filtering statements

    rest = filterfalse(factory_is_any_isinstance(AST_IMPORTS), ast_obj.body)

    # finalize extraction
    source_code = '\n'.join(map(unparse, rest))

    return source_code


def find_nonlocal_imports(ast_obj, local_modules):
    # filtering statements
    imps = filter(factory_is_any_isinstance(AST_IMPORTS), ast_obj.body)

    # finalize extraction
    nonlocal_imports = '\n'.join(filter_imports(imps, local_modules))

    return nonlocal_imports


def filter_imports(imps, forbidden):
    for imp in imps:
        if isinstance(imp, ast.ImportFrom):
            m = import_module(imp.module)
            f = find_file(m)
            if f is None or not is_any_samefile(f, forbidden):
                yield unparse(imp)
        elif isinstance(imp, ast.Import):
            for nm in imp.names:
                m = import_module(nm.name)
                f = find_file(m)
                if f is None or not is_any_samefile(f, forbidden):
                    yield unparse(ast.Import([nm]))
        else:
            assert False, 'Impossible!'


def find_file(obj):
    if obj is None:
        return None
    module = getmodule(obj)

    if module is None:
        return None
    try:
        return Path(getfile(module))
    except TypeError:
        return None


def prepare_template():
    tpl = Path('extra/template.py.tpl')
    ds_names = [name for name, _ in collect_datasets()]
    tplpy = tpl.with_suffix('')

    s = tpl.read_text()
    s = s.replace('DATASETS_FUNCTIONS', f'[{", ".join(ds_names)}]')
    tplpy.write_text(s)

    return tplpy


def assert_clashed_names(enriched):
    saved = dict()
    has_clashed = False
    for p, (_, _, names) in enriched:
        for nm in names:
            if nm in saved:
                has_clashed = True
                log.error(f'Name "{nm}" from "{p}" clashed with "{saved[nm]}"')
            else:
                saved[nm] = p
    assert not has_clashed, 'Some names are not unique!'


def main():
    log.basicConfig(level=log.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
    mdl_caller = Path('pre_definition/solve_caller.py')
    mdl_tag = Path('pre_definition/tag.py')
    mdl_stdio = Path('pre_definition/stdio.py')
    mdl_params = Path('pre_definition/params.py')

    mdl_common = Path('implementation/common.py')
    mdl_checker = Path('implementation/checker.py')
    mdl_generator = Path('implementation/generator.py')
    mdl_solution = Path('implementation/solver.py')

    mdl_template = prepare_template()

    local_modules = [
        mdl_caller,
        mdl_tag,
        mdl_stdio,
        mdl_params,
        mdl_common,
        mdl_checker,
        mdl_generator,
        mdl_solution,
        mdl_template,
    ]
    enriched = [(m, parse_module(m, local_modules)) for m in local_modules]

    assert_clashed_names(enriched)

    mpy = Path('my.py')

    with stdio(output=mpy.open('w')):
        for _, (imps, _, _) in enriched:
            print(imps)

        for _, (_, codes, _) in enriched:
            print(codes)


if __name__ == '__main__':
    main()
