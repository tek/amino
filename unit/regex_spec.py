from amino.test import Spec
from amino.regex import Regex
from amino import List


class RegexSpec(Spec):

    def match(self):
        n1 = 'grp1'
        n2 = 'grp2'
        r = Regex('pre:(?P<{}>\w+)/(\w+)%(\w+)'.format(n1))
        g1 = List.random_string()
        g2 = List.random_string()
        g3 = List.random_string()
        s = 'pre:{}/{}%{}'.format(g1, g2, g3)
        res = r.match(s)
        res.should.be.right
        m = res.value
        m.g(n1).should.contain(g1)
        m.g(n2).should.be.empty
        m.l.should.equal(List(g1, g2, g3))

__all__ = ('RegexSpec',)
