from typing import Callable, TypeVar, Generic

from tryp import Either, Right, Left

A = TypeVar('A')


class Task(Generic[A]):

    def __init__(self, f: Callable[[], A]) -> None:
        self.run = f

    def unsafePerformSync(self) -> Either[Exception, A]:
        try:
            return Right(self.run())
        except Exception as e:
            return Left(e)


def Try(f: Callable[..., A], *a, **kw) -> Either[Exception, A]:
    return Task(lambda: f(*a, **kw)).unsafePerformSync()

__all__ = ('Task', 'Try')
