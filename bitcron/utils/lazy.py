# coding: utf8
from __future__ import absolute_import
import re
import json
import os

def curry(_curried_func, *args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return _curried_func(*(args+moreargs), **dict(kwargs, **morekwargs))
    return _curried


def to_number(value, default_if_fail=None, max_value=None, number_type_func=None):
    if not value and type(value)!=int:
        return default_if_fail
    try:
        value = float(value)
        if number_type_func:
            value = number_type_func(value)
    except:
        value = default_if_fail
    if max_value and value>max_value:
        value = max_value
    return value

to_float = curry(to_number, number_type_func=None)
to_int = curry(to_number, number_type_func=int)


def is_int(value):
    if isinstance(value, bool):
        return False
    elif isinstance(value, int):
        return True
    elif isinstance(value, (str, unicode)):
        value = value.strip()
        if re.match('^\d+$', value):
            return True
        else:
            return False
    else:
        return False


def is_float(value):
    if isinstance(value, float):
        return True
    elif isinstance(value, (str, unicode)):
        value = value.strip()
        if re.match('^\d*\.\d*$', value):
            return True
        else:
            return False
    else:
        return False


def auto_float(value):
    # 严格意义的float
    if is_float(value):
        return to_float(value)
    else:
        return value

def auto_int(value):
    # 严格意义的int
    if is_int(value):
        return to_int(value)
    else:
        return value


def auto_bool(value):
    # 严格意义的true/false
    if isinstance(value, (str, unicode)):
        if value.lower() == 'false':
            value = False
        elif value.lower() == 'true':
            return True
    return value


def auto_value(value):
    value = auto_float(value)
    value = auto_int(value)
    value = auto_bool(value)
    return value


def get_value_by_index(value, index):
    try:
        return value[index]
    except IndexError:
        return None



def load_json_from_filepath(filepath):
    if not os.path.isfile(filepath):
        return
    try:
        with open(filepath) as f:
            return json.loads(f.read())
    except:
        return

def dump_json_to_filepath(data, filepath):
    try:
        with open(filepath, 'w') as f:
            f.write(json.dumps(data))
    except:
        pass



def split_list(ls, size_per_part):
    for i in range(0, len(ls), size_per_part):
        yield ls[i:i + size_per_part]