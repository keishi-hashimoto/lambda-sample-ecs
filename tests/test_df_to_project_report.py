import sys

import pytest

sys.path.append("..")
from typing import TypeAlias

import polars as pl

from lambda_function import ManHour, WeeklyProjectReport, df_to_project_report

Df: TypeAlias = pl.DataFrame


@pytest.mark.parametrize(
    argnames=["df", "expected"],
    argvalues=[
        pytest.param(
            Df(
                {
                    "Pコード": ["A001"],
                    "案件名": ["開発案件A"],
                    "名前": ["太郎"],
                    "工数": [4.0],
                }
            ),
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[ManHour(name="太郎", hour=4.0)],
                )
            ],
            id="Only one row.",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": ["A001", "A001"],
                    "案件名": ["開発案件A", "開発案件A"],
                    "名前": ["太郎", "次郎"],
                    "工数": [4.0, 2.0],
                }
            ),
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[
                        ManHour(name="太郎", hour=4.0),
                        ManHour(name="次郎", hour=2.0),
                    ],
                )
            ],
            id="One project, two members.",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": ["A001", "B001"],
                    "案件名": ["開発案件A", "開発案件B"],
                    "名前": ["太郎", "次郎"],
                    "工数": [4.0, 2.0],
                }
            ),
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[
                        ManHour(name="太郎", hour=4.0),
                    ],
                ),
                WeeklyProjectReport(
                    project_code="B001",
                    name="開発案件B",
                    man_hours=[
                        ManHour(name="次郎", hour=2.0),
                    ],
                ),
            ],
            id="Two projects, one member for each.",
        ),
        pytest.param(
            Df(
                {
                    "Pコード": ["A001", "B001", "A001", "B001"],
                    "案件名": ["開発案件A", "開発案件B", "開発案件A", "開発案件B"],
                    "名前": ["太郎", "次郎", "次郎", "太郎"],
                    "工数": [4.0, 2.0, 1.3, 4.5],
                }
            ),
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[
                        ManHour(name="太郎", hour=4.0),
                        ManHour(name="次郎", hour=1.3),
                    ],
                ),
                WeeklyProjectReport(
                    project_code="B001",
                    name="開発案件B",
                    man_hours=[
                        ManHour(name="次郎", hour=2.0),
                        ManHour(name="太郎", hour=4.5),
                    ],
                ),
            ],
            id="Two projects, two members for each, random order.",
        ),
    ],
)
def test(df: Df, expected: list[WeeklyProjectReport]):
    actual = df_to_project_report(df)
    assert actual == expected
