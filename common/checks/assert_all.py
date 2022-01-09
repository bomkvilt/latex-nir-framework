from typing import Literal


_CHECKS = {
    'true':     lambda x: x == True,
    'non-none': lambda x: x != None,
}


def assert_all(*values, mode=Literal['true', 'non-none']):
    check = _CHECKS[mode]
    for value in values:
        assert(check(value))
