import sys

import pytest

sys.path.append("..")
from typing import TypeAlias

import polars as pl
from polars.testing import assert_frame_equal

from lambda_function import add_project_name_to_df

Df: TypeAlias = pl.DataFrame

DUMMY_PROJECT_MAP_DF = Df(
    {"Pコード": ["A001", "B002"], "案件名": ["保守案件1", "開発案件A"]}
)


@pytest.mark.parametrize(
    argnames=["df", "expected"],
    argvalues=[
        pytest.param(
            Df(
                {
                    "Pコード": ["A001"],
                    "名前": ["太郎"],
                    "工数": [4.0],
                }
            ),
            Df(
                {
                    "Pコード": ["A001"],
                    "案件名": ["保守案件1"],
                    "名前": ["太郎"],
                    "工数": [4.0],
                }
            ),
            id="Only one row",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": ["A001", "B002"],
                    "名前": ["太郎", "太郎"],
                    "工数": [4.0, 2.0],
                }
            ),
            Df(
                {
                    "Pコード": ["A001", "B002"],
                    "案件名": ["保守案件1", "開発案件A"],
                    "名前": ["太郎", "太郎"],
                    "工数": [4.0, 2.0],
                }
            ),
            id="Multiple Projects",
        ),
    ],
)
def test_normal(df: Df, expected: Df):
    actual = add_project_name_to_df(df, DUMMY_PROJECT_MAP_DF)
    assert_frame_equal(actual, expected)
