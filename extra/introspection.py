import logging as log
from typing import Callable as ABCCallable

from impl import generator as generators
from impl import wrong as wrongs


def collect_datasets():
    datasets = []
    for name, obj in generators.__dict__.items():
        if not isinstance(obj, ABCCallable):
            continue
        if hasattr(obj, 'is_dataset'):
            log.debug(f'Dataset "{name}" has been collected')
            datasets.append((name, obj))

    log.info(f'Total datasets groups: {len(datasets)}')
    assert len(datasets) > 0, 'No datasets'

    return datasets


def collect_wrong_solutions():
    wrsols = []
    for name, obj in wrongs.__dict__.items():
        if not isinstance(obj, ABCCallable):
            continue
        if hasattr(obj, 'is_wrong'):
            log.debug(f'Wrong solution "{name}" has been collected')
            wrsols.append((name, obj))

    log.info(f'Total wrong solutions: {len(wrsols)}')
    assert len(wrsols) > 0, 'No wrong solutions'

    return wrsols
