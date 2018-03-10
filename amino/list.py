from typing import TypeVar, Callable

from amino.data.list import List, Lists, Nil
from amino import Eval, Maybe, Nothing, Just, __

A = TypeVar('A')


def replace_one(fa: List[A], pred: Callable[[A], bool], new: A) -> Eval[Maybe[List[A]]]:
    def loop(head: A, tail: List[A]) -> Eval[Maybe[List[A]]]:
        def flatten(memla: Maybe[Eval[Maybe[List[A]]]]) -> Eval[Maybe[List[A]]]:
            return (
                memla
                .map(lambda emla: emla.map(lambda mla: mla.map(lambda la: la.cons(head)))) |
                (lambda: Eval.now(Nothing))
            )
        return (
            Eval.now(Just(tail.cons(new)))
            if pred(head) else
            Eval.later(tail.detach_head.map2, loop) // flatten
        )
    return fa.detach_head.map2(loop) | Eval.now(Nothing)


__all__ = ('List', 'Lists', 'Nil')
