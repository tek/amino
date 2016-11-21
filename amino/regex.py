import re

from amino import L, _, Maybe, Map, List


class Regex:

    def __init__(self, spec) -> None:
        self.spec = spec
        self.rex = re.compile(spec)

    def __getattr__(self, name):
        if hasattr(self.rex, name):
            return getattr(self.rex, name)
        else:
            raise AttributeError('Regex has no attribute \'{}\''.format(name))

    def match(self, data, *a, **kw) -> Maybe['Match']:
        return (
            Maybe(self.rex.match(data, *a, **kw))
            .to_either('`{}` does not match `{}`'.format(data, self.spec)) /
            L(Match)(self, _, data)
        )


class Match:

    def __init__(self, regex: Regex, internal, data: str) -> None:
        self.regex = regex
        self.internal = internal

    @property
    def group_map(self):
        return Map(self.internal.groupdict())

    m = group_map

    def group(self, id):
        return self.group_map.get(id)

    g = group

    @property
    def groups(self):
        return List.wrap(self.internal.groups())

    l = groups

    @property
    def match(self):
        return self.internal.group(0)

__all__ = ('Regex',)
