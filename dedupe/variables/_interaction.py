from __future__ import annotations

import itertools
from typing import Mapping, Sequence

from dedupe.__typing import VariableDefinition
from dedupe.variables._base import FieldType as FieldVariable, Variable


class InteractionType(Variable):
    type = "Interaction"
    higher_vars: list['InteractionType']

    def __init__(self, definition: VariableDefinition):

        if definition.interaction_variables is None:
            raise ValueError(
                "'interaction_variables' can not be None for variable "
                f"{definition.name} of type {definition.type}"
            )
        self.interactions = definition.interaction_variables
        self.name = "(Interaction: %s)" % str(self.interactions)
        self.interaction_fields = self.interactions

        super().__init__(definition)

    def expandInteractions(self, field_model: Mapping[str, FieldVariable]) -> None:

        self.interaction_fields = self.atomicInteractions(
            self.interactions, field_model
        )
        for field in self.interaction_fields:
            if field_model[field].has_missing:
                self.has_missing = True

        self.categorical(field_model)

    def categorical(self, field_model: Mapping[str, FieldVariable]) -> None:
        categoricals = [
            field
            for field in self.interaction_fields
            if hasattr(field_model[field], "higher_vars")
        ]
        noncategoricals = [
            field
            for field in self.interaction_fields
            if not hasattr(field_model[field], "higher_vars")
        ]

        dummies = [field_model[field].higher_vars for field in categoricals]

        self.higher_vars = []
        for combo in itertools.product(*dummies):
            var_names = [field.name for field in combo] + noncategoricals
            var_def = VariableDefinition(
                -1,
                "__interaction__",
                has_missing=self.has_missing,
                interaction_variables=var_names
            )

            higher_var = InteractionType(
                # {"has missing": self.has_missing, "interaction variables": var_names}
                var_def
            )
            self.higher_vars.append(higher_var)

    def atomicInteractions(
        self,
        interactions: Sequence[str],
        field_model: Mapping[str, FieldVariable]
    ) -> list[str]:
        atomic_interactions = []

        for field in interactions:
            try:
                field_model[field]
            except KeyError:
                raise KeyError(
                    "The interaction variable %s is "
                    "not a named variable in the variable "
                    "definition" % field
                )

            if hasattr(field_model[field], "interaction_fields"):
                sub_interactions = field_model[field].interaction_fields  # type: ignore[attr-defined]
                atoms = self.atomicInteractions(sub_interactions, field_model)
                atomic_interactions.extend(atoms)
            else:
                atomic_interactions.append(field)

        return atomic_interactions
