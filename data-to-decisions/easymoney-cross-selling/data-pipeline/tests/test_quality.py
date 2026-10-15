import pytest

from easymoney_pipeline.quality import (
    DataQualityError, check_binary, check_in_domain, check_no_orphans,
    check_no_parse_loss, check_not_null, check_row_count, check_unique,
)


@pytest.fixture
def df(spark):
    return spark.createDataFrame(
        [(1, "A", 0), (2, "B", 1), (3, None, 1)], "id int, cat string, flag int")


def test_check_unique_passes(df):
    assert check_unique(df, ["id"]) == 3


def test_check_unique_fails_on_duplicates(df):
    with pytest.raises(DataQualityError, match="duplicates"):
        check_unique(df.union(df.limit(1)), ["id"])


def test_check_not_null(df):
    check_not_null(df, ["id", "flag"])
    with pytest.raises(DataQualityError, match="cat"):
        check_not_null(df, ["cat"])


def test_check_in_domain(df):
    check_in_domain(df, "flag", [0, 1])
    check_in_domain(df, "cat", ["A", "B"], allow_null=True)
    with pytest.raises(DataQualityError):
        check_in_domain(df, "cat", ["A", "B"])   # nulls rejected by default
    with pytest.raises(DataQualityError):
        check_in_domain(df, "flag", [0])


def test_check_binary(spark):
    check_binary(spark.createDataFrame([(0, 1), (1, 0)], "a int, b int"), ["a", "b"])
    bad = spark.createDataFrame([(0, 2), (None, 1)], "a int, b int")
    with pytest.raises(DataQualityError, match="'a': 1, 'b': 1"):
        check_binary(bad, ["a", "b"])


def test_check_no_parse_loss(spark):
    df = spark.createDataFrame(
        [("2018-01", 1), (None, None), ("bad", None)], "raw string, parsed int")
    with pytest.raises(DataQualityError, match="1 non-null"):
        check_no_parse_loss(df, "raw", "parsed")
    check_no_parse_loss(df.filter("raw IS NULL OR raw != 'bad'"), "raw", "parsed")


def test_check_row_count(df):
    assert check_row_count(df, 3, "toy") == 3
    with pytest.raises(DataQualityError, match="expected 4"):
        check_row_count(df, 4, "toy")


def test_check_no_orphans(spark, df):
    parent = spark.createDataFrame([(1,), (2,), (3,)], "id int")
    check_no_orphans(df, parent, "id")
    with pytest.raises(DataQualityError):
        check_no_orphans(df, parent.filter("id < 3"), "id")