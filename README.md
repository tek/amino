## About
This library provides some functional data structures, utilities and a typeclass system that resemble those concepts in
scala.
Most of the implementations have considerable overhead and aren't suitable for performance critical applications; their
purpose is nicer and familiar syntax and composability.

## Anonymous functions
These are an alternative to `lambda`s with parameter placeholder wildcards and literal string representation.

```python
from amino import L, _, __

f = L(isinstance)(_, str)
f('amino')
# True

# for methods
f = __.index('n')
f('amino')
# 3

# for attributes
f = _.parent
f(Path('/home/user'))
# Path('/home')
```

## Data

### List
A wrapper for stdlib `list` with extended interface.

```python
from amino import List, _

l = List(1, 2, 3, 4)
l.map(_ + 5)
# List(6, 7, 8, 9)

l = List(List(1, 2), List(3, 4))
l.flat_map(__.map(_ - 1))
# List(0, 1, 2, 3)
```

### Maybe
An optional ADT with subtypes `Just` and `Empty`.

```python
j = Just(1)
e = Empty()

j.map(List)
# Just(List(1))

e.map(_ + 2)
# Empty()

j.flat_map(L(Just)(_ - 2))
# Just(-1)
```

### Either
A simple coproduct type that can be inhabited by two types.

```python
r = Right(5)
l = Left('error')

r.map(_ + 1)
# Right(6)

l.map(_ + 1)
# Left('error')

l.lmap(_ + ' in test')
# Left('error in test')

r.flat_map(lambda a: Left(a + 3))
# Left(8)
```

## Typeclasses
Although these make a lot more sense with a real type system, they provide a nice abstraction for functionality.
The `map` and `flat_map` operations, for instance, are implemented in the typeclasses `Functor` and `FlatMap`, for which
instances are provided for arbitrary types, among them `List` and `Maybe`.
The typeclasses define methods that are looked up in the data class' `__getattr__`, which is provided by the `Implicits`
base class inherited by `List` and `Maybe`.
The typeclass instances are stored in a global registry, which can be used separately from the `Implicits` concept:

```python
from amino.tc.monad import Monad

Monad.lookup(List).flat_map(List(1, 2), _ + 5)
# List(6, 7)
```

Instances can be registered in several ways, the easiest of which is by passing the target type to the metaclass:

```python
from typing import TypeVar, Callable
from amino.tc.functor import Functor

A = TypeVar('A')
B = TypeVar('B')

class ListFunctor(Functor, tpe=List):

  def map(l: List[A], f: Callable[[A], B]) -> List[B]:
    return List.wrap(map(f, l))
```

After importing the instance's module, the `map` method can be used as shown
above.

## IO
`IO` is a trampolined algebra for computation abstraction that catches errors:

```python
t = IO.now(Path('/var/log/dmesg')).flat_map(L(IO.delay)(__.read_text()))
# IO(Now(/var/log/dmesg).flat_map(L(delay)(__.read_text())))

t.attempt
# Right('...'): Either[TaskException, str]
# or
# Left(TaskException('Now(/var/log/dmesg).flat_map(L(delay)(__.read_text()))', [], PermissionError(13, 'Permission denied')))
```
