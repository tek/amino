## About
This library provides some functional data structures, utilities and a typeclass system that resemble those concepts in
scala.
Some of the implementations have considerable overhead and aren't suitable for performance critical applications; their
purpose is nicer and familiar syntax and composability.

## Anonymous functions
These are an alternative to `lambda`s with parameter placeholder wildcards.
If the env var `AMINO_ANON_DEBUG` is set, a different implementation with severe performance penalties but literal
string representation is used.

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

j.flat_map(lambda a: Just(a - 2))
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

## do notation
The function decorator `do` allows to use generators as do-blocks with any class that responds to `flat_map`.
It is implemented by looping until the generator is exhausted, calling `flat_map` on each yielded effect and sending
its value into the generator.

```python
from amino import do

@do(Either[int, int])
def compute() -> Do:
  user = yield Right('root')
  content = yield IO.delay(Path('/etc/passwd').read_text).attempt
  yield Lists.lines(content).index_where(lambda l: user in l).to_either('not found')
```

All yielded values produce an Either, the return value is the found index or the error message from the last statement
or the `IO` call.

`return a` behaves similar to Haskell, being equivalent to `yield Monad[F].pure(a)`.

## Typeclasses
Although these make a lot more sense with a real type system, they provide a nice abstraction for functionality.
The `map` and `flat_map` operations, for instance, are implemented in the typeclasses `Functor` and `FlatMap`, for which
instances are provided for arbitrary types, among them `List` and `Maybe`.
The typeclasses define methods that are looked up in the data class' `__getattr__`, which is provided by the `Implicits`
base class inherited by `List` and `Maybe`.
The typeclass instances are stored in a global registry, which can be used separately from the `Implicits` concept:

```python
from amino.tc.monad import Monad

Monad.lookup(List).flat_map(List(1, 2), lambda a: List(a + 5))
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
t = IO.pure(Path('/var/log/dmesg')).flat_map(L(IO.delay)(__.read_text()))
# IO(Pure(/var/log/dmesg).flat_map(L(delay)(__.read_text())))

t.attempt
# Right('...'): Either[IOException, str]
# or
# Left(IOException('Pure(/var/log/dmesg).flat_map(L(delay)(__.read_text()))', [], PermissionError(13, 'Permission denied')))
```

## StateT
`StateT` abstracts `F[S => F[S, A]]`, implemented for several effects as `EitherState` etc.
It offers the usual monadic constructors:

```python
from amino.state import StateT, EitherState

@do
def state(x: int) -> typing.Generator[StateT[Either, str, int], Any, None]:
  i = yield EitherState.inspect_f(lambda s: Try(int, s))
  yield EitherState.modify(lambda a: len(a) * x + i)
  yield EitherState.pure(x)

s = state(5)
s.run('15') # -> Right((25, 5))
```

## Data
The base class `Dat` makes working with pure data types simpler by analyzing a class' `__init__` and creating class attributes containing info about its fields.
This allows for simple copying (optionally with type check) without intrusive descriptor magic – a `Dat` instance is
still a plain old python object.

```python
class Data(Dat['Data'])

    def __init__(a: int, b: List[str]) -> None:
        self.a = a
        self.b = b

Data(7, List('one', 'two')).copy(a=3)
```

## Json

*amino* provides a framework for Json de/encoding based on typeclasses.
The functions `encode_json`, `dump_json` and `decode_json` look for instances of the typeclasses `Encoder` and `Decoder` to
process data.
Codecs for some builtins like `Path` and `UUID` as well as *amino's standard types like `Either` and `Maybe` are provided.

The most convenient aspect of this is that `Dat` will automatically call the corresponding De/Encoder for all its
fields, making serialization of nested data structures trivial.
