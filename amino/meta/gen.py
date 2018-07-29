import re
from typing import Tuple

from amino import Path, IO, do, Do, Dat, List


class CodegenTask(Dat['CodegenTask']):

    @staticmethod
    def cons(
            template: Path,
            subs: List[Tuple[str, str]],
            imports: List[str],
    ) -> 'CodegenTask':
        return CodegenTask(
            template,
            subs,
            imports,
        )

    def __init__(
            self,
            template: Path,
            subs: List[Tuple[str, str]],
            imports: List[str],
    ) -> None:
        self.template = template
        self.subs = subs
        self.imports = imports


@do(IO[str])
def codegen(task: CodegenTask) -> Do:
    template_path = yield IO.delay(task.template.absolute)
    template_code = yield IO.delay(template_path.read_text)
    replaced = task.subs.fold_left(template_code)(lambda z, a: re.sub(a[0], a[1], z))
    return task.imports.cat(replaced).join_lines


@do(IO[str])
def codegen_write(task: CodegenTask, outpath: Path) -> Do:
    code = yield codegen(task)
    yield IO.delay(outpath.write_text, code)
    return code


__all__ = ('CodegenTask', 'codegen', 'codegen_write',)
