"""Transformation logic shared by the pipeline notebooks."""
import re

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F


def clean_col(name: str) -> str:
    """Lowercase and replace invalid chars with '_' (Delta-safe names)."""
    name = re.sub(r"[^0-9a-z_]", "_", name.strip().lower())
    return name or "_unnamed"


def to_binary_flag(col: str) -> Column:
    """'0', '1.0', NULL -> int 0/1. NULL means product not held."""
    return F.coalesce(F.col(col).cast("double").cast("int"), F.lit(0))


def split_segment(col: str) -> tuple[Column, Column]:
    """'03 - UNIVERSITARIO' -> (3, 'UNIVERSITARIO'). Unparseable code -> NULL."""
    code = F.expr(f"try_cast(split({col}, ' - ')[0] AS INT)")
    name = F.trim(F.split(F.col(col), " - ").getItem(1))
    return code, name


def add_customer_timeline(df: DataFrame, target: str) -> DataFrame:
    """Per-customer lead/lag context on customer_monthly.

    A gap in monthly snapshots invalidates next/prev (has_next / has_prev = False).
    ever_had_before only looks at months strictly before t.
    """
    w = Window.partitionBy("customer_id").orderBy("partition_month")
    w_hist = w.rowsBetween(Window.unboundedPreceding, -1)
    return (df
        .withColumn("next_month", F.lead("partition_month").over(w))
        .withColumn("next_flag", F.lead(target).over(w))
        .withColumn("prev_month", F.lag("partition_month").over(w))
        .withColumn("prev_n_products", F.lag("n_products").over(w))
        .withColumn("prev_is_active", F.lag("is_active").over(w))
        .withColumn("ever_had_before", F.coalesce(F.max(target).over(w_hist), F.lit(0)))
        .withColumn("has_next", F.coalesce(
            F.col("next_month") == F.add_months("partition_month", 1), F.lit(False)))
        .withColumn("has_prev", F.coalesce(
            F.col("prev_month") == F.add_months("partition_month", -1), F.lit(False)))
    )


def align_sales_to_snapshot(sales: DataFrame, product_ids: DataFrame) -> DataFrame:
    """Sale in month t+1 -> label keyed on snapshot month t."""
    return (sales
        .join(product_ids, "product_id")
        .select("customer_id", F.add_months("sale_month", -1).alias("partition_month"))
        .distinct()
        .withColumn("has_sale_next_month", F.lit(1)))