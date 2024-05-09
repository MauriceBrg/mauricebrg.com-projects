import decimal
import typing


class PurchasedItem(typing.TypedDict):
    """Describes an item that has been purchased from Amazon"""

    id: str
    description: str
    category: typing.Literal["physical", "digital", "membership"]
    price: decimal.Decimal
    refunded: bool
    timestamp: str
    year: int
    month: int
    day_of_month: int
    day_of_week: int
