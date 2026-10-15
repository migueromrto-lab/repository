import sys
from pathlib import Path

import pytest
from pyspark.sql import SparkSession

# Make easymoney_pipeline importable wherever pytest is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session")
def spark():
    return SparkSession.getActiveSession() or SparkSession.builder.getOrCreate()