from fn import _  # type: ignore

from tryp.test import Spec

from tryp import Map, Empty, Just


class Map_(Spec):

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

    def add_multi(self):
        key = 'key'
        val = 'value'
        k2 = 'key2'
        v2 = 'value2'
        m = Map({key: val})
        m2 = m ** Map({k2: v2})
        m2.get(k2).should.equal(Just(v2))
        m.get(k2).should.equal(Empty())

    def find(self):
        k1 = 'key'
        v1 = 'value'
        k2 = 'key2'
        v2 = 'value2'
        m = Map({k1: v1, k2: v2})
        m.find(_ == v1).should.equal(Just((k1, v1)))
        m.find_key(_ == k2).should.equal(Just((k2, v2)))
        m.find(_ == 'invalid').should.equal(Empty())
        m.find_key(_ == 'invalid').should.equal(Empty())

    def map(self):
        k1 = 'key'
        v1 = 'value'
        k2 = 'key2'
        v2 = 'value2'
        m = Map({k1: v1, k2: v2})
        res = m.map(lambda a: (len(a[0]), len(a[1])))
        res.should.have.key(len(k1)).being.equal(len(v1))
        res.should.have.key(len(k2)).being.equal(len(v2))

    def keymap(self):
        k1 = 'key'
        v1 = 'value'
        k2 = 'key2'
        v2 = 'value2'
        m = Map({k1: v1, k2: v2})
        res = m.keymap(lambda a: len(a))
        res.should.have.key(len(k1)).being.equal(v1)
        res.should.have.key(len(k2)).being.equal(v2)

    def flat_map(self):
        k1 = 'key'
        v1 = 'value'
        k2 = 'key2'
        v2 = 'value2'
        m = Map({k1: v1, k2: v2})
        res = m.flat_map(lambda a, b: Just((a, b)) if a == k1 else Empty())
        res.should.have.key(k1).being.equal(v1)
        res.should_not.have.key(k2)

__all__ = ['Map_']
