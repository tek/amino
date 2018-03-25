import os
import sys
import subprocess


def compile(path: str) -> None:
    if subprocess.run(['coconut', '--target', '3.6', '--quiet', '--strict', path]).returncode != 0:
        print('failed to compile coco files')
        sys.exit(1)


def compile_coco_projects() -> None:
    return
    if 'COCO_DIRS' in os.environ and 'AMINO_COMPILE_COCO' in os.environ:
        for dir in os.environ.get('COCO_DIRS', '').split(':'):
            compile(dir)

__all__ = ('compile_coco_projects',)
