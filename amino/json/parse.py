#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x40340b99

# Compiled with Coconut version 1.3.0 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop
import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_NamedTuple, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_pipe, _coconut_star_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: -----------------------------------------------------------

import json
from typing import Any

from amino import Either
from amino import Left
from amino import Lists
from amino import Map
from amino import Try
from amino.json.data import Json
from amino.json.data import JsonArray
from amino.json.data import JsonScalar
from amino.json.data import JsonObject


def to_json(a: 'Any') -> 'Json':
    _coconut_match_to = a
    _coconut_match_check = False
    if _coconut.isinstance(_coconut_match_to, (list, tuple)):
        a = _coconut_match_to
        _coconut_match_check = True
    if _coconut_match_check:
        result = JsonArray(Lists.wrap(a) / to_json)
    if not _coconut_match_check:
        if _coconut.isinstance(_coconut_match_to, dict):
            a = _coconut_match_to
            _coconut_match_check = True
        if _coconut_match_check:
            result = JsonObject(Map(a).valmap(to_json))
    if not _coconut_match_check:
        a = _coconut_match_to
        _coconut_match_check = True
        if _coconut_match_check:
            result = JsonScalar(a)
    return result


def parse_json(payload: 'str') -> 'Either[str, Json]':
    return Try(json.loads, payload) / to_json
