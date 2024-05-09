import argparse
import collections
import decimal
import hashlib
import json
import pathlib


from entities import PurchasedItem
from utils import get_date_components, get_non_schema_files_matching_glob

PRIME_MEMBERSHIP_TITLE = '"Prime Membership Fee"'


def get_digital_items(base_dir: pathlib.Path) -> list[PurchasedItem]:
    """
    Returns a list of purchased digital items.
    """

    id_to_purchased_item: dict[str, PurchasedItem] = {}

    for file in get_non_schema_files_matching_glob(
        base_dir, "DigitalOrders.DigitalItems.*.json"
    ):
        print("Processing", file)

        with open(file, "r", encoding="utf-8") as f:
            digital_items = json.load(f)

            for item in digital_items:

                p_item: PurchasedItem = {
                    "id": item["digitalOrderItemId"],
                    "category": (
                        "digital"
                        if item["title"] != PRIME_MEMBERSHIP_TITLE
                        else "membership"
                    ),
                    "description": str(item["title"]).strip('"'),
                    "timestamp": item["eventDate"],
                    "price": decimal.Decimal("0"),
                    "refunded": False,
                }

                (
                    p_item["year"],
                    p_item["month"],
                    p_item["day_of_month"],
                    p_item["day_of_week"],
                ) = get_date_components(p_item["timestamp"])

                id_to_purchased_item[p_item["id"]] = p_item

                if item.get("quantityOrdered", 1) > 1:
                    raise RuntimeError("Can't handle digital orders with quantity > 1")

    for file in get_non_schema_files_matching_glob(
        base_dir, "DigitalOrders.DigitalOrdersMonetary.*.json"
    ):

        print("Processing", file)

        with open(file, "r", encoding="utf-8") as f:
            digital_items = json.load(f, parse_float=decimal.Decimal)

        for item in digital_items:
            _id = item["digitalOrderItemId"]

            id_to_purchased_item[_id]["price"] += item["transactionAmount"]

    # TODO: Handle returns

    return list(id_to_purchased_item.values())


def get_physical_items(base_dir: pathlib.Path) -> list[PurchasedItem]:
    """
    Returns a list of purchased physical items.
    """

    id_to_purchased_item: dict[str, PurchasedItem] = {}
    order_id_to_purchased_items: dict[str, list[PurchasedItem]] = (
        collections.defaultdict(list)
    )

    for file in get_non_schema_files_matching_glob(
        base_dir, "Orders.OrderHistory.*.json"
    ):
        print("Processing", file)

        with open(file, "r", encoding="utf-8") as f:
            orders_returned = json.load(f, parse_float=decimal.Decimal)

            for item in orders_returned:

                p_item: PurchasedItem = {
                    "id": item["orderId"]
                    + hashlib.sha256(item["productName"].encode("utf-8")).hexdigest(),
                    "category": "physical",
                    "description": str(item["productName"]).strip('"'),
                    "timestamp": item["eventDate"],
                    "price": item["totalOwed"],
                    "refunded": False,
                }

                (
                    p_item["year"],
                    p_item["month"],
                    p_item["day_of_month"],
                    p_item["day_of_week"],
                ) = get_date_components(p_item["timestamp"])

                id_to_purchased_item[p_item["id"]] = p_item
                order_id_to_purchased_items[item["orderId"]].append(p_item)

                if item.get("quantity", 1) > 1:
                    p_item["description"] = (
                        f'{item.get("quantity", 1)} x {p_item["description"]} (Price is total)'
                    )
                    p_item["price"] *= item.get("quantity", 1)

    for file in get_non_schema_files_matching_glob(
        base_dir, "Orders.OrdersReturned.Payments.*.json"
    ):
        print("Processing", file)

        with open(file, "r", encoding="utf-8") as f:
            orders_returned = json.load(f, parse_float=decimal.Decimal)

            for item in orders_returned:
                order_id = item["orderId"]
                refund_amount = decimal.Decimal(item["amountRefunded"])

                purchases = order_id_to_purchased_items[order_id]

                for purchase in purchases:
                    # Not sure if partial refunds exist, but they may make this inaccurate
                    if purchase["price"] == refund_amount:
                        purchase["refunded"] = True

    return list(id_to_purchased_item.values())


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description="Parse an Amazon Data Export and create a report."
    )

    parser.add_argument(
        "REPORT_DIR", type=str, help="Path to the Unzipped Report files"
    )

    parser.add_argument(
        "OUTPUT_FILE",
        type=argparse.FileType("w", encoding="utf-8"),
        help="Filename to save the changes under.",
    )

    return parser


def main():

    parser = build_parser()

    args = parser.parse_args()

    path = pathlib.Path(args.REPORT_DIR)

    digital_items = get_digital_items(path)
    physical_items = get_physical_items(path)

    all_purchased_items = digital_items + physical_items

    print("Writing purchased items to", args.OUTPUT_FILE.name)
    json.dump(all_purchased_items, args.OUTPUT_FILE, default=str)


if __name__ == "__main__":
    main()
