"""Tests to figure out what's the fastest way to hash a dataframe."""
import abc
import csv
import functools
import hashlib
import logging
import statistics
import sys
import typing

from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, date
from decimal import Decimal

import numpy as np
import pandas as pd
import pandas.testing

LOGGER = logging.getLogger()

# The hash function to use to create hashes over columns.
# All functions in hashlib should work, but there are performance trade-offs.
HASH_FUNCTION: typing.Callable = hashlib.sha256
# Used as a separator when concating fields for hashing, ensures there are no
# mistakes if fields are empty.
HASH_FIELD_SEPARATOR: str = ":"

ITERATIONS_PER_N_RECORDS_PER_HASHER = 5

MEASUREMENTS = defaultdict(list)

@functools.lru_cache(10)
def build_dataframe(n_rows: int) -> pd.DataFrame:
    """Builds a dataframe with 5 columns and n_rows rows that has a mix of columns."""

    np.random.seed(42)

    input_df = pd.DataFrame(
        np.random.choice(['foo','bar','baz', Decimal("1.333"), 11, False], size=(n_rows, 5))
    )
    input_df = input_df.set_axis(['A', 'B', 'C', 'D', 'E'], axis=1, inplace=False)
    LOGGER.info("Created dataframe with shape %s", input_df.shape)
    return input_df

@contextmanager
def log_and_record_runtime(task: str, hasher: str, num_records: int):
    """Contextmanager that logs the runtime of a piece of code."""

    start = datetime.now()
    # LOGGER.info("Task: '%s' starts", task)

    yield

    runtime = (datetime.now() - start).total_seconds()

    LOGGER.info("Task '%s' took %.4f seconds", task, runtime)

    MEASUREMENTS[(hasher, num_records)].append(runtime)


class AbstractHasher(abc.ABC):
    """Interface for structured testing."""

    dataframe: pd.DataFrame
    target_column_name: str
    columns_to_hash: typing.List[str]
    num_records: int


    def __init__(self, dataframe: pd.DataFrame,
        columns_to_hash: typing.List[str], target_column_name: str) -> 'AbstractHasher':

        self.dataframe = dataframe.copy()
        self.target_column_name = target_column_name
        self.columns_to_hash = columns_to_hash
        self.num_records = len(dataframe)

    def run_and_measure(self, n_times: int) -> None:
        """Run the Hasher n_times and log the runtimes."""

        for _ in range(n_times):
            hasher = self.__class__.__name__
            log_msg = f"Run {hasher} with {self.num_records} records"
            with log_and_record_runtime(log_msg, hasher, self.num_records):
                self.hash()

    @abc.abstractmethod
    def hash(self) -> pd.DataFrame:
        """Hash the columns"""

class PandasApplyHasher0(AbstractHasher):
    """The original implementation"""

    def hash(self) -> pd.DataFrame:

        def hash_columns(row: pd.Series) -> str:

            values = row[self.columns_to_hash]
            pre_hash = HASH_FIELD_SEPARATOR.join(
                str(value) for value in values)

            hashed_values = HASH_FUNCTION(
                pre_hash.encode("utf-8")).hexdigest()

            return hashed_values

        self.dataframe[self.target_column_name] = \
            self.dataframe.apply(hash_columns, axis=1)

        return self.dataframe

class PandasApplyHasher1(AbstractHasher):
    """The first implementation from the project"""

    def hash(self) -> pd.DataFrame:

        def hash_columns(row: pd.Series) -> str:
            values = row[self.columns_to_hash]
            pre_hash = HASH_FIELD_SEPARATOR.join(str(value) for value in values.to_list())
            hashed_values = HASH_FUNCTION(pre_hash.encode("utf-8")).hexdigest()
            return hashed_values

        self.dataframe[self.target_column_name] = self.dataframe.apply(hash_columns, axis=1)

        return self.dataframe

class PandasApplyHasher2(AbstractHasher):
    """Avoid slicing from the dataframe many times."""

    def hash(self) -> pd.DataFrame:

        def hash_columns(row: pd.Series) -> str:
            pre_hash = HASH_FIELD_SEPARATOR.join(map(str, row.to_list()))
            hashed_values = HASH_FUNCTION(pre_hash.encode("utf-8")).hexdigest()
            return hashed_values

        # We run the apply on only the columns relevant for the hash
        # This means we slice once and not n times.
        self.dataframe[self.target_column_name] = \
            self.dataframe[self.columns_to_hash].apply(hash_columns, axis=1)

        return self.dataframe

class PandasApplyHasher3(AbstractHasher):
    """Avoid conversion to list."""

    def hash(self) -> pd.DataFrame:

        def hash_columns(row: pd.Series) -> str:
            pre_hash = HASH_FIELD_SEPARATOR.join(row.apply(str))
            hashed_values = HASH_FUNCTION(pre_hash.encode("utf-8")).hexdigest()
            return hashed_values

        self.dataframe[self.target_column_name] = \
            self.dataframe[self.columns_to_hash].apply(hash_columns, axis=1)

        return self.dataframe

class PandasApplyHasher4(AbstractHasher):
    """Apply str to series directly"""

    def hash(self) -> pd.DataFrame:

        def hash_columns(row: pd.Series) -> str:
            pre_hash = HASH_FIELD_SEPARATOR.join(map(str, row))
            hashed_values = HASH_FUNCTION(pre_hash.encode("utf-8")).hexdigest()
            return hashed_values

        self.dataframe[self.target_column_name] = \
            self.dataframe[self.columns_to_hash].apply(hash_columns, axis=1)

        return self.dataframe

class PandasApplyHasher5(AbstractHasher):
    """List comprehension instead of map."""

    def hash(self) -> pd.DataFrame:

        def hash_columns(row: pd.Series) -> str:
            pre_hash = HASH_FIELD_SEPARATOR.join([str(value) for value in row])
            hashed_values = HASH_FUNCTION(pre_hash.encode("utf-8")).hexdigest()
            return hashed_values

        self.dataframe[self.target_column_name] = \
            self.dataframe[self.columns_to_hash].apply(hash_columns, axis=1)

        return self.dataframe

class NativePythonHasher0(AbstractHasher):
    """Avoid the pandas apply and do things inside python"""

    def hash(self) -> pd.DataFrame:

        list_of_records = self.dataframe[self.columns_to_hash]\
            .to_records(index=False)

        def hash_record(record: np.recarray) -> str:
            pre_hash = HASH_FIELD_SEPARATOR.join(map(str, record))
            hashed_values = HASH_FUNCTION(pre_hash.encode("utf-8")).hexdigest()
            return hashed_values

        hashes = [hash_record(record) for record in list_of_records]

        self.dataframe[self.target_column_name] = hashes

        return self.dataframe

HASHERS_TO_TEST = [
    PandasApplyHasher0,
    PandasApplyHasher1,
    PandasApplyHasher2,
    PandasApplyHasher3,
    PandasApplyHasher4,
    PandasApplyHasher5,
    NativePythonHasher0,
]

def assert_hasher_is_correct(hasher_class: typing.Type[AbstractHasher]) -> None:
    """Assert that a given hasher computes the output we expect for known inputs."""

    # Arrange

    known_input = pd.DataFrame({
        "int": [1, 2, 3],
        "decimal": [Decimal("1.33"), Decimal("7"), Decimal("23.5")],
        "bool": [True, False, True],
        "date": [date.fromisoformat("2022-09-16"), date.fromisoformat("2022-04-13"),
            date.fromisoformat("2022-09-16")],
        "str": ["This", "Hasher", "Is_Correct"],
    })

    expected_df = known_input.copy()
    expected_df["hashed"] = [
        "c1551c906a6e8ebeecb91abbfd90db87264f1335cd4e855d3c8521b7c02c8c65",
        "0afe31f8a139e9dfe7466989f7b4ffdb6504b150c81949f72bd96875b0ae91c4",
        "073ccefe4bc389dd6b97321f5467305c910f14dfba58f4d75c9f9a67eed43514"
    ]

    columns_to_hash = ["int", "decimal", "bool", "date", "str"]
    target_column_name = "hashed"

    # Act

    hasher = hasher_class(
        dataframe=known_input,
        columns_to_hash=columns_to_hash,
        target_column_name=target_column_name,
    )

    actual_df = hasher.hash()

    # Assert

    pandas.testing.assert_frame_equal(actual_df, expected_df)
    LOGGER.info("Hasher %s is correct", hasher_class.__name__)



def performance_test_hashers(n_records: int):
    """Performance test all hashers with n_records."""

    kwargs = {
        "dataframe": build_dataframe(n_records),
        "columns_to_hash": ["A", "B", "C", "D", "E"],
        "target_column_name": "hash_value"
    }

    for hasher in HASHERS_TO_TEST:

        hasher_instance = hasher(**kwargs)
        hasher_instance.run_and_measure(ITERATIONS_PER_N_RECORDS_PER_HASHER)

def measurements_as_list_for_csv() -> None:
    """Turn the measurements into a list fit for a csv."""

    csv_output = [
        ["hasher", "n_records", "min", "max", "mean", "median"]
    ]

    for key, values in MEASUREMENTS.items():

        hasher, n_records = key
        min_value = min(values)
        max_value = max(values)
        mean_value = statistics.mean(values)
        median_value = statistics.median(values)

        csv_output.append([hasher, n_records, min_value, max_value, mean_value, median_value])

    return csv_output

def main() -> None:
    """Function that orchestrates the tests."""
    LOGGER.addHandler(
        logging.StreamHandler(sys.stdout)
    )
    LOGGER.setLevel(logging.INFO)

    # There is no point in testing incorrect hashers.
    for hasher in HASHERS_TO_TEST:
        assert_hasher_is_correct(hasher)

    for n_records in [1, 10_000, 100_000, 250_000, 500_000]:
        performance_test_hashers(n_records)

    csv_list = measurements_as_list_for_csv()

    with open("hasher_measurements.csv", "w", encoding="utf-8") as file:

        writer = csv.writer(file, delimiter=";", quotechar='"')
        writer.writerows(csv_list)

if __name__ == "__main__":
    main()
