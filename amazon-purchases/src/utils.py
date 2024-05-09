import typing

from datetime import date
from pathlib import Path


def get_date_components(datetime_str: str) -> tuple[int, int, int, int]:
    """
    Returns year, month, day of month and day of week from an ISO8601 formatted string.

    get_date_components("2023-09-19T20:24:37.493Z")

    will return:

    2023, 9, 19, 1
    """

    dt = date.fromisoformat(datetime_str.split("T")[0])

    return dt.year, dt.month, dt.day, dt.weekday()


def get_non_schema_files_matching_glob(
    base_dir: Path, glob_pattern: str
) -> typing.Iterator[Path]:

    for file in base_dir.glob(glob_pattern):
        if ".schema." in file.name:
            continue

        yield file


if __name__ == "__main__":
    print(get_date_components("2023-09-19T20:24:37.493Z"))
