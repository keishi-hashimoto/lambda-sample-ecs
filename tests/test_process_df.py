import sys
from typing import TypeAlias

import polars as pl
import pytest
from polars.testing import assert_frame_equal

sys.path.append("..")
from lambda_function import process_df

Df: TypeAlias = pl.DataFrame

base = {
    "Pコード": ["A001", "A001", "B002", "B002"],
    "名前": ["太郎", "太郎", "太郎", "次郎"],
    "日付": ["4/1", "4/2", "4/1", "4/2"],
    "工数": [4, 2, 4, 1.0],
}


@pytest.mark.parametrize(
    argnames=["df", "expected"],
    argvalues=[
        pytest.param(
            Df(
                {
                    "Pコード": ["A001"],
                    "名前": ["太郎"],
                    "日付": ["4/1"],
                    "工数": [4.0],
                }
            ),
            Df(
                {
                    "Pコード": ["A001"],
                    "名前": ["太郎"],
                    "工数": [4.0],
                }
            ),
            id="Only one row",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": ["A001", "A001"],
                    "名前": ["太郎", "太郎"],
                    "日付": ["4/1", "4/2"],
                    "工数": [4.0, 2.0],
                }
            ),
            Df(
                {
                    "Pコード": ["A001"],
                    "名前": ["太郎"],
                    "工数": [6.0],
                }
            ),
            id="One project, one member, two date.",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": ["A001", "A001"],
                    "名前": ["太郎", "次郎"],
                    "日付": ["4/1", "4/2"],
                    "工数": [4.0, 2.0],
                }
            ),
            Df(
                {
                    "Pコード": ["A001", "A001"],
                    "名前": ["太郎", "次郎"],
                    "工数": [4.0, 2.0],
                }
            ),
            id="One project, two members, one date for each.",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": ["A001", "B002"],
                    "名前": ["太郎", "太郎"],
                    "日付": ["4/1", "4/1"],
                    "工数": [4.0, 2.0],
                }
            ),
            Df(
                {
                    "Pコード": ["A001", "B002"],
                    "名前": ["太郎", "太郎"],
                    "工数": [4.0, 2.0],
                }
            ),
            id="Two projects, one member, one date for each.",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": [
                        "A001",
                        "B002",
                        "A001",
                        "B002",
                        "A001",
                        "B002",
                        "A001",
                        "B002",
                    ],
                    "名前": [
                        "太郎",
                        "太郎",
                        "太郎",
                        "太郎",
                        "次郎",
                        "次郎",
                        "次郎",
                        "次郎",
                    ],
                    "日付": ["4/1", "4/2", "4/2", "4/3", "4/1", "4/2", "4/2", "4/3"],
                    "工数": [4.0, 2.0, 1.5, 3.0, 4.0, 2.0, 1.5, 3.0],
                }
            ),
            Df(
                {
                    "Pコード": ["A001", "B002", "A001", "B002"],
                    "名前": ["太郎", "太郎", "次郎", "次郎"],
                    "工数": [5.5, 5.0, 5.5, 5.0],
                }
            ),
            id="Two projects, two members, two dates for each.",
        ),
    ],
)
def test(df: Df, expected: Df):
    actual = process_df(df)
    assert_frame_equal(actual, expected)
