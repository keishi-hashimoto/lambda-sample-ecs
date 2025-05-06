import sys

import pytest

sys.path.append("..")
from typing import TypeAlias

import polars as pl

from lambda_function import validate_project_code

Df: TypeAlias = pl.DataFrame

DUMMY_PROJECT_MAP_DF = Df(
    {"Pコード": ["A001", "A002"], "案件名": ["保守案件1", "開発案件2"]}
)


@pytest.mark.parametrize(
    argnames=["df"],
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
            id="Valid project code.",
        )
    ],
)
def test_valid_project_name(df: Df):
    validate_project_code(df, DUMMY_PROJECT_MAP_DF)


@pytest.mark.parametrize(
    argnames=["df", "expected_error"],
    argvalues=[
        pytest.param(
            Df(
                {
                    "Pコード": ["C001"],
                    "名前": ["太郎"],
                    "日付": ["4/1"],
                    "工数": [4.0],
                }
            ),
            "以下の P コードは不正です\n\n* C001",
            id="Invalid project code.",
        )
    ],
)
def test_invalid_project_name(df: Df, expected_error: str):
    with pytest.raises(ValueError) as e:
        validate_project_code(df, DUMMY_PROJECT_MAP_DF)

    assert str(e.value) == expected_error
