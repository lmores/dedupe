from dataclasses import dataclass, field
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Collection,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Mapping,
    Sequence,
    Tuple,
    Type,
    Union,
)

import numpy as np
import numpy.typing as npt

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, TypedDict
else:
    from typing_extensions import Literal, Protocol, TypedDict


if TYPE_CHECKING:
    from dedupe._predicates import Predicate

RecordPK = Union[int, str]
RecordID = int
RecordIDDType = Union[Type[int], Tuple[Type[str], Literal[256]]]
RecordIDPair = Tuple[RecordID, RecordID]
Record = Sequence[Any]  # Tuple[RecordID, RecordDict]
RecordPair = Tuple[Record, Record]
RecordPairs = Iterator[RecordPair]
RecordPairsList = List[RecordPair]
Block = Sequence[RecordPair]
Blocks = Iterator[Block]

NpFloatArray = npt.NDArray[np.float_]
Cluster = Tuple[Tuple[RecordID, ...], Union[NpFloatArray, Tuple[float, ...]]]
Clusters = Iterable[Cluster]
Data = Sequence[Record] # Mapping[RecordID, RecordDict]
Links = Iterable[Union[np.ndarray, Tuple[Tuple[RecordID, RecordID], float]]]
LookupResults = Iterable[Tuple[RecordID, Tuple[Tuple[RecordID, float], ...]]]
JoinConstraint = Literal["one-to-one", "many-to-one", "many-to-many"]
Comparator = Callable[[Any, Any], Union[int, float, Sequence[Union[int, float]]]]
Scores = Union[np.memmap, np.ndarray]
Labels = List[Literal[0, 1]]
LabelsLike = Iterable[Literal[0, 1]]
Cover = Dict['Predicate', FrozenSet[int]]
ComparisonCover = Dict['Predicate', FrozenSet[Tuple[RecordID, RecordID]]]
PredicateFunction = Callable[[Any], Iterable[str]]
# Takes pairs of records and generates a (n_samples X n_features) array
FeaturizerFunction = Callable[[Sequence[RecordPair]], NpFloatArray]
MapLike = Callable[[Callable[[Any], Any], Iterable], Iterable]


@dataclass
class VariableDefinition:
    # field: str
    field_index: int
    type: str

    categories: Sequence[str] | None = None
    # a custom comparator can only return float or int
    comparator: Callable[[Any, Any], Union[int, float]] | None = None
    corpus: Iterable[Union[str, Collection[str]]] | None = None
    crf: bool = False
    has_missing: bool = False
    interaction_variables: Sequence[str] | None = None
    name: str | None = None
    other_fields: Sequence[int] | None = None
    variable_name: str | None = None


@dataclass(frozen=True, slots=True)
class TrainingData:
    match: List[RecordPair] = field(default_factory=list)
    distinct: List[RecordPair] = field(default_factory=list)


class Classifier(Protocol):
    """Take an array of distances and compute the likelihood of the associated pair."""

    def fit(self, X: NpFloatArray, y: LabelsLike) -> None:
        pass

    def predict_proba(self, X: NpFloatArray) -> NpFloatArray:
        pass


class ClosableJoinable(Protocol):
    def close(self) -> None:
        pass

    def join(self) -> None:
        pass
