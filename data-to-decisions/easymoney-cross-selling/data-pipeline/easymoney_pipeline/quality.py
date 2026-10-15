"""Reusable data quality checks for the easyMoney pipeline.

Each check raises DataQualityError on failure and returns a value on success.
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


class DataQualityError(Exception):
    """Blocking data quality failure."""


def check_unique(df: DataFrame, keys: list[str]) -> int:
    """Grain check: one row per key combination."""
    n_rows = df.count()
    n_keys = df.select(*keys).distinct().count()
    if n_rows != n_keys:
        raise DataQualityError(f"{n_rows - n_keys:,} duplicates on {keys}")
    return n_rows


def check_not_null(df: DataFrame, cols: list[str]) -> None:
    """Mandatory columns must have no nulls."""
    counts = df.agg(*[F.sum(F.col(c).isNull().cast("int")).alias(c) for c in cols]).first().asDict()
    bad = {c: n for c, n in counts.items() if n}
    if bad:
        raise DataQualityError(f"Nulls in mandatory columns: {bad}")


def check_in_domain(df: DataFrame, col: str, allowed: list, allow_null: bool = False) -> None:
    """Values must belong to the allowed set."""
    cond = ~F.col(col).isin(list(allowed))
    if not allow_null:
        cond = cond | F.col(col).isNull()
    n_bad = df.filter(cond).count()
    if n_bad:
        raise DataQualityError(f"{n_bad:,} values of '{col}' outside {list(allowed)}")


def check_binary(df: DataFrame, cols: list[str]) -> None:
    """Flag columns must be 0/1 with no nulls. Single pass over the data."""
    counts = df.agg(*[
        F.sum((F.col(c).isNull() | ~F.col(c).isin(0, 1)).cast("int")).alias(c) for c in cols
    ]).first().asDict()
    bad = {c: n for c, n in counts.items() if n}
    if bad:
        raise DataQualityError(f"Non-binary values: {bad}")


def check_no_parse_loss(df: DataFrame, raw_col: str, parsed_col: str) -> None:
    """A non-null raw value must not turn into NULL after parsing."""
    n = df.filter(F.col(raw_col).isNotNull() & F.col(parsed_col).isNull()).count()
    if n:
        raise DataQualityError(f"{n:,} non-null '{raw_col}' values lost parsing into '{parsed_col}'")


def check_row_count(df: DataFrame, expected: int, label: str) -> int:
    """Row count reconciliation between layers."""
    n = df.count()
    if n != expected:
        raise DataQualityError(f"{label}: {n:,} rows, expected {expected:,}")
    return n


def check_no_orphans(child: DataFrame, parent: DataFrame, key: str) -> None:
    """Referential integrity: every child key must exist in parent."""
    n = child.join(parent.select(key).distinct(), key, "left_anti").count()
    if n:
        raise DataQualityError(f"{n:,} rows with '{key}' missing in parent table")