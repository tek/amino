import json
from typing import Any

from amino import Either, Lists, Map, Try
from amino.json.data import Json, JsonArray, JsonScalar, JsonObject, JsonNull, JsonError


def to_json(a: Any) -> Json:
    return (
        JsonArray(Lists.wrap(a) / to_json)
        if isinstance(a, (list, tuple)) else
        JsonObject(Map(a).valmap(to_json))
        if isinstance(a, dict) else
        JsonNull(None)
        if a is None else
        JsonScalar(a)
    )


def parse_json(payload: str) -> Either[str, Json]:
    return (Try(json.loads, payload) / to_json).lmap(lambda e: JsonError(payload, e))
