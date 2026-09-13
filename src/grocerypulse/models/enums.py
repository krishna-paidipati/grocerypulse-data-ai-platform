from enum import StrEnum


class StoreFormat(StrEnum):
	EXPRESS = "EXPRESS"
	SUPERMARKET = "SUPERMARKET"
	SUPERSTORE = "SUPERSTORE"
	EXTRA = "EXTRA"
	FULFILLMENT_CENTRE = "FULFILLMENT_CENTRE"


class CustomerSegment(StrEnum):
    VALUE = "VALUE"
    FAMILY = "FAMILY"
    PREMIUM = "PREMIUM"
    CONVENIENCE = "CONVENIENCE"
    OTHER = "OTHER"


class SalesChannel(StrEnum):
    STORE = "STORE"
    WEB = "WEB"
    APP = "APP"


class SupplierType(StrEnum):
    LOCAL = "LOCAL"
    REGIONAL = "REGIONAL"
    NATIONAL = "NATIONAL"
    IMOPORTER = "IMPORTER"

class UnitMeasure(StrEnum):
    L = "L"
    ML = "ML"
    KG = "KG"
    G = "G"
    EACH = "EA"

class ProductCategory(StrEnum):
    DAIRY = "DAIRY"
    BAKERY = "BAKERY"
    FROZEN = "FROZEN"
    PRODUCE = "PRODUCE"
    MEAT = "MEAT"
    BEVERAGES = "BEVERAGES"
    GROCERY = "GROCERY"
    PERSONAL_CARE = "PERSONAL_CARE"
    HOUSEHOLD = "HOUSEHOLD"


