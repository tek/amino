from typing import Callable, TypeVar, Generic

from tryp import Either, Right, Left

A = TypeVar('A')


class Task(Generic[A]):

    @staticmethod
    def call(f: Callable[..., A], *a, **kw):
        return Task(lambda: f(*a, **kw))

    def __init__(self, f: Callable[[], A]) -> None:
        self.run = f

    def unsafe_perform_sync(self) -> Either[Exception, A]:
        try:
            return Right(self.run())
        except Exception as e:
            return Left(e)


def Try(f: Callable[..., A], *a, **kw) -> Either[Exception, A]:
    return Task.call(f, *a, **kw).unsafe_perform_sync()

__all__ = ('Task', 'Try')
