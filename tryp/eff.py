from typing import Callable

from tryp import List, I, __, L, _


class Eff:
    ''' An effect stack transformer.
    Wraps arbitrarily nested effects, like Task[List[Maybe[A]]].
    '''

    def __init__(self, value, effects: List[type]=List(), depth: int=1
                 ) -> None:
        self.value = value
        self.effects = effects.cons(type(value))
        self.depth = depth

    def _map(self, f: Callable):
        g = List.wrap(range(self.depth)).fold_left(f)(lambda z, i: __.map(z))
        return g(self.value)

    def map(self, f: Callable):
        return Eff(self._map(__.map(f)), self.effects, self.depth)

    __truediv__ = map

    def _flat_map(self, f: Callable):
        ''' **f** must return the same stack type as **self.value** has.
        Iterates over the effects, sequences the inner instance
        successively to the top and joins with the outer instance.
        Example:
        List(Right(Just(1))) => List(Right(Just(List(Right(Just(5))))))
        => List(List(Right(Just(Right(Just(5))))))
        => List(Right(Just(Right(Just(5)))))
        => List(Right(Right(Just(Just(5)))))
        => List(Right(Just(Just(5))))
        => List(Right(Just(5)))
        Note: Task works only as outermost effect, as it cannot sequence
        '''
        index = List.range(self.depth + 1)
        g = index.fold_left(f)(lambda z, i: __.map(z))
        nested = g(self.value)
        def sequence_level(z, depth, tpe):
            nesting = lambda z, i: __.map(z).sequence(tpe)
            lifter = List.range(depth).fold_left(I)(nesting)
            return z // lifter
        def sequence_type(z, data):
            return L(sequence_level)(_, *data).map(z)
        h = self.effects.reversed.with_index.fold_left(I)(sequence_type)
        return h(nested)

    def flat_map(self, f: Callable):
        ''' Calls **f** with the inner values, if present, and sequences
        the result, which is assumed to be a complete stack, one by one
        through the old stack.
        '''
        return Eff(self._flat_map(f), self.effects)

    __floordiv__ = flat_map

    def flat_map_inner(self, f: Callable):
        return Eff(self.value.map(__.flat_map(f)), self.effects, self.depth)

__all__ = ('Eff',)
