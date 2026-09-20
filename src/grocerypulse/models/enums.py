"""Canonical enumerations used by GroceryPulse domain contracts.

Code Owner:
    Vijay Krishna Paidipati

Component:
    Canonical Data Contracts

Purpose:
    Defines controlled vocabularies used across GroceryPulse so equivalent
    business concepts are represented consistently by producers, storage
    layers, transformations, APIs, and analytical workloads.
"""

from enum import StrEnum


class StoreFormat(StrEnum):
    """Supported GroceryPulse physical and fulfilment store formats."""

    EXPRESS = "EXPRESS"
    SUPERMARKET = "SUPERMARKET"
    SUPERSTORE = "SUPERSTORE"
    EXTRA = "EXTRA"
    FULFILLMENT_CENTRE = "FULFILLMENT_CENTRE"


class CustomerSegment(StrEnum):
    """Business-defined customer segmentation categories."""

    VALUE = "VALUE"
    FAMILY = "FAMILY"
    PREMIUM = "PREMIUM"
    CONVENIENCE = "CONVENIENCE"
    OTHER = "OTHER"


class SalesChannel(StrEnum):
    """Supported GroceryPulse sales channels."""

    STORE = "STORE"
    WEB = "WEB"
    APP = "APP"


class SupplierType(StrEnum):
    """Business-defined supplier types."""

    LOCAL = "LOCAL"
    REGIONAL = "REGIONAL"
    NATIONAL = "NATIONAL"
    IMPORTER = "IMPORTER"


class UnitMeasure(StrEnum):
    """Supported unit measures for product pricing and inventory."""

    L = "L"
    ML = "ML"
    KG = "KG"
    G = "G"
    EACH = "EA"


class ProductCategory(StrEnum):
    """Business-defined product categories."""

    DAIRY = "DAIRY"
    BAKERY = "BAKERY"
    FROZEN = "FROZEN"
    PRODUCE = "PRODUCE"
    MEAT = "MEAT"
    BEVERAGES = "BEVERAGES"
    GROCERY = "GROCERY"
    PERSONAL_CARE = "PERSONAL_CARE"
    HOUSEHOLD = "HOUSEHOLD"
