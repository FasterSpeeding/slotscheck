from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, fields
from itertools import chain, filterfalse
from typing import (
    Any,
    Callable,
    Collection,
    Iterable,
    Mapping,
    Set,
    Tuple,
    TypeVar,
)

flatten = chain.from_iterable


_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_Ttype = TypeVar("_Ttype", bound=type)


# adapted from itertools recipe
def unique(iterable: Iterable[_T1]) -> Iterable[_T1]:
    "List unique elements, preserving order."
    seen: Set[_T1] = set()
    seen_add = seen.add
    for element in filterfalse(seen.__contains__, iterable):
        seen_add(element)
        yield element


def groupby(
    it: Iterable[_T1], *, key: Callable[[_T1], _T2]
) -> Mapping[_T2, Collection[_T1]]:
    "Group items into a dict by key"
    grouped = defaultdict(list)
    for i in it:
        grouped[key(i)].append(i)

    return grouped


@dataclass(frozen=True, repr=False)
class compose:
    "Funtion composition"
    __slots__ = ("_functions",)
    _functions: Tuple[Callable[[Any], Any], ...]

    def __init__(self, *functions: Any) -> None:
        object.__setattr__(self, "_functions", functions)

    def __call__(self, value: Any) -> Any:
        for f in reversed(self._functions):
            value = f(value)
        return value


# Adapted from dataclasses.dataclass_tools
# Under Apache license 2.0
# Changed only `dataclass.fields` naming
def add_slots(cls: _Ttype) -> _Ttype:  # pragma: no cover
    # Need to create a new class, since we can't set __slots__
    #  after a class has been created.

    # Make sure __slots__ isn't already set.
    if "__slots__" in cls.__dict__:
        raise TypeError(f"{cls.__name__} already specifies __slots__")

    # Create a new dict for our new class.
    cls_dict = dict(cls.__dict__)
    field_names = tuple(f.name for f in fields(cls))
    cls_dict["__slots__"] = field_names
    for field_name in field_names:
        # Remove our attributes, if present. They'll still be
        #  available in _MARKER.
        cls_dict.pop(field_name, None)
    # Remove __dict__ itself.
    cls_dict.pop("__dict__", None)
    # And finally create the class.
    qualname = getattr(cls, "__qualname__", None)
    cls = type(cls)(cls.__name__, cls.__bases__, cls_dict)
    if qualname is not None:
        cls.__qualname__ = qualname
    return cls
