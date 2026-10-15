import datetime as dt

from easymoney_pipeline.transforms import (
    add_customer_timeline, align_sales_to_snapshot,
    clean_col, split_segment, to_binary_flag,
)


def d(s):
    return dt.date.fromisoformat(s)


def test_clean_col():
    assert clean_col(" Product ID ") == "product_id"
    assert clean_col("em-acount") == "em_acount"
    assert clean_col("   ") == "_unnamed"


def test_to_binary_flag(spark):
    df = spark.createDataFrame([(1, "0"), (2, "1.0"), (3, None)], "id int, v string")
    out = df.select("id", to_binary_flag("v").alias("f")).orderBy("id").collect()
    assert [r.f for r in out] == [0, 1, 0]


def test_split_segment(spark):
    df = spark.createDataFrame(
        [(1, "03 - UNIVERSITARIO"), (2, "XX - BAD"), (3, None)], "id int, s string")
    code, name = split_segment("s")
    out = df.select("id", code.alias("code"), name.alias("name")).orderBy("id").collect()
    assert [(r.code, r.name) for r in out] == [(3, "UNIVERSITARIO"), (None, "BAD"), (None, None)]


def test_add_customer_timeline(spark):
    rows = [
        (1, d("2018-01-01"), 0, 1, 1),
        (1, d("2018-02-01"), 1, 2, 1),
        (1, d("2018-04-01"), 0, 1, 0),   # March missing
    ]
    df = spark.createDataFrame(
        rows, "customer_id int, partition_month date, pension_plan int, n_products int, is_active int")
    out = {r.partition_month: r for r in add_customer_timeline(df, "pension_plan").collect()}
    jan, feb, apr = out[d("2018-01-01")], out[d("2018-02-01")], out[d("2018-04-01")]

    assert jan.has_next and jan.next_flag == 1 and not jan.has_prev
    assert not feb.has_next                              # next snapshot not consecutive
    assert feb.has_prev and feb.ever_had_before == 0     # current month excluded from history
    assert not apr.has_prev and apr.ever_had_before == 1


def test_align_sales_to_snapshot(spark):
    sales = spark.createDataFrame(
        [(1, d("2018-03-01"), 1364), (1, d("2018-03-01"), 1364), (2, d("2018-03-01"), 2335)],
        "customer_id int, sale_month date, product_id int")
    products = spark.createDataFrame([(1364,)], "product_id int")
    out = align_sales_to_snapshot(sales, products).collect()

    assert len(out) == 1                                 # dedup + product filter
    assert out[0].customer_id == 1 and out[0].partition_month == d("2018-02-01")