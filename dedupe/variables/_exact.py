from typing import Any

from dedupe import _predicates
from dedupe.variables._base import FieldType


class ExactType(FieldType):
    _predicate_functions = [_predicates.wholeFieldPredicate]
    type = "Exact"

    @staticmethod
    def comparator(field_1: Any, field_2: Any) -> int:
        if field_1 == field_2:
            return 1
        else:
            return 0
