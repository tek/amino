import sure  # NOQA
from flexmock import flexmock  # NOQA

from tek import Spec  # type: ignore

from tryp import Map, Empty, Just


class Map_(Spec, ):

    def setup(self, *a, **kw):
        super(Map_, self).setup(*a, **kw)

    def get(self):
        key = 'key'
        val = 'value'
        m = Map({key: val})
        m.get(key).should.equal(Just(val))
        m.get(key + key).should.equal(Empty())

    def add(self):
        key = 'key'
        val = 'value'
        k2 = 'key2'
        v2 = 'value2'
        m = Map({key: val})
        m2 = m + (k2, v2)
        m2.get(k2).should.equal(Just(v2))
        m.get(k2).should.equal(Empty())

    def addMulti(self):
        key = 'key'
        val = 'value'
        k2 = 'key2'
        v2 = 'value2'
        m = Map({key: val})
        m2 = m ** Map({k2: v2})
        m2.get(k2).should.equal(Just(v2))
        m.get(k2).should.equal(Empty())

__all__ = ['Map_']
