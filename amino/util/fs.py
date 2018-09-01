from amino import Path, IO


def mkdir(path: Path) -> IO[None]:
    return IO.delay(path.mkdir, parents=True, exist_ok=True)


__all__ = ('create_dir',)
