"""Shared base configuration for GroceryPulse domain models.

Code Owner:
    Vijay Krishna Paidipati

Component:
    Canonical Data Contracts

Purpose:
    Defines validation behaviour that is consistently inherited by all
    GroceryPulse Pydantic domain models.

Developer Notes:
    Changes to this configuration can affect every canonical entity and
    therefore require regression testing of generated schemas and consumers.
"""

from pydantic import BaseModel, ConfigDict


class GroceryPulseModel(BaseModel):
    """Base class for all canonical GroceryPulse Pydantic models.

    The model enforces strict schema behaviour across the platform:

    * Unknown attributes are rejected.
    * Surrounding whitespace is removed from strings.
    * Assignment after object construction is revalidated.

    These rules reduce accidental schema drift between producers and
    downstream consumers.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )
