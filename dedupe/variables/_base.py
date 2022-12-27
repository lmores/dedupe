from __future__ import annotations

from typing import TYPE_CHECKING

from dedupe import _predicates

if TYPE_CHECKING:
    from typing import Any, ClassVar, Generator, Iterable, Sequence, Type

    from dedupe.__typing import Comparator, PredicateFunction, VariableDefinition


class Variable(object):
    type: ClassVar[str]

    name: str
    predicates: list[_predicates.Predicate]
    higher_vars: Sequence['Variable']

    def __len__(self) -> int:
        return 1

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        other_name: str = other.name
        return self.name == other_name

    def __init__(self, definition: VariableDefinition):
        if definition.has_missing:
            self.has_missing = True
            try:
                exists_pred = _predicates.ExistsPredicate(definition.field_index)
                self.predicates.append(exists_pred)
            except KeyError:
                pass
        else:
            self.has_missing = False

    def __getstate__(self) -> dict[str, Any]:
        odict = self.__dict__.copy()
        odict["predicates"] = None

        return odict

    @classmethod
    def all_subclasses(
        cls,
    ) -> Generator[tuple[str | None, Type['Variable']], None, None]:
        for q in cls.__subclasses__():
            yield getattr(q, "type", None), q
            for p in q.all_subclasses():
                yield p


class DerivedType(Variable):
    type = "Derived"

    def __init__(self, definition: VariableDefinition):
        self.name = "(%s: %s)" % (definition.name, definition.type)
        super(DerivedType, self).__init__(definition)


class MissingDataType(Variable):
    type = "MissingData"

    def __init__(self, name: str):
        self.name = "(%s: Not Missing)" % name
        self.has_missing = False


class FieldType(Variable):
    _index_thresholds: Sequence[float] = []
    _index_predicates: Sequence[Type[_predicates.IndexPredicate]] = []
    _predicate_functions: Sequence[PredicateFunction] = ()
    _Predicate: Type[_predicates.SimplePredicate] = _predicates.SimplePredicate
    comparator: Comparator

    def __init__(self, definition: VariableDefinition):
        self.field_index = definition.field_index

        if definition.variable_name is not None:
            self.name = definition.variable_name
        else:
            self.name = "(%s: %s)" % (self.field_index, self.type)

        self.predicates = [
            self._Predicate(pred, self.field_index) for pred in self._predicate_functions
        ]

        self.predicates += indexPredicates(
            self._index_predicates, self._index_thresholds, self.field_index
        )

        super(FieldType, self).__init__(definition)


class CustomType(FieldType):
    type = "Custom"

    def __init__(self, definition: VariableDefinition):
        super(CustomType, self).__init__(definition)

        if definition.comparator is None:
            raise KeyError(
                "For 'Custom' field types you must define a "
                "'comparator' function in the field definition. "
            )
        self.comparator = definition.comparator  # type: ignore[assignment]

        if definition.variable_name is None:
            self.name = "(%s: %s, %s)" % (
                self.field_index,
                self.type,
                self.comparator.__name__,
            )


def indexPredicates(
    predicates: Iterable[Type[_predicates.IndexPredicate]],
    thresholds: Sequence[float],
    field_index: int,
) -> list[_predicates.IndexPredicate]:
    index_predicates = []
    for predicate in predicates:
        for threshold in thresholds:
            index_predicates.append(predicate(threshold, field_index))

    return index_predicates
