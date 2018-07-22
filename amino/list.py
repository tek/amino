from typing import TypeVar, Callable, Tuple

from amino.data.list import List, Lists, Nil
from amino import Eval, Maybe, Nothing, Just, __, Either

A = TypeVar('A')
B = TypeVar('B')


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


def split_by_status_zipped(data: List[Tuple[A, bool]]) -> Tuple[List[A], List[A]]:
    def decide(z: Tuple[List[A], List[A]], item: Tuple[A, bool]) -> Tuple[List[A], List[A]]:
        l, r = z
        a, status = item
        return (
            (l.cat(a), r)
            if status else
            (l, r.cat(a))
        )
    return data.fold_left((Nil, Nil))(decide)


def split_by_status(data: List[A], statuses: List[bool]) -> Tuple[List[A], List[A]]:
    return split_by_status_zipped(data.zip(statuses))


def split_either_list(data: List[Either[A, B]]) -> Tuple[List[A], List[B]]:
    def split(z: Tuple[List[A], List[B]], a: Either[A, B]) -> Tuple[List[A], List[B]]:
        ls, rs = z
        return a.cata((lambda e: (ls.cat(e), rs)), (lambda v: (ls, rs.cat(v))))
    return data.fold_left((Nil, Nil))(split)


__all__ = ('List', 'Lists', 'Nil', 'split_by_status', 'split_by_status_zipped', 'split_either_list',)
