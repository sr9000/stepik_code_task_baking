import logging as log
import shutil


def clear_dir(dsdir):
    for item in dsdir.iterdir():
        log.debug(f'Deleting "{item}"')
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
            else:
                raise Exception(f'Nor dir or file item "{item}"')
        except Exception:
            log.exception(f'Failed to delete "{item}"')
            quit(-1)

    log.info(f'Directory "{dsdir}" has been cleared')
