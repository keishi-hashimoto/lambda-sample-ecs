import sys
from textwrap import dedent

import pytest

sys.path.append("..")
from typing import TypeAlias

import polars as pl

from lambda_function import ManHour, WeeklyProjectReport, report_to_msg

Df: TypeAlias = pl.DataFrame


@pytest.mark.parametrize(
    argnames=["reports", "expected"],
    argvalues=[
        pytest.param(
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[ManHour(name="太郎", hour=4.0)],
                )
            ],
            """
            # 工数週次レポート
            
            ## [A001] 開発案件A
            
            - 太郎 さん: 4.0 時間
            - **合計: 4.0 時間**
            """,
            id="One project, one member.",
        ),
        pytest.param(
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[
                        ManHour(name="太郎", hour=4.0),
                        ManHour(name="次郎", hour=1.5),
                    ],
                )
            ],
            """
            # 工数週次レポート
            
            ## [A001] 開発案件A
            
            - 太郎 さん: 4.0 時間
            - 次郎 さん: 1.5 時間
            - **合計: 5.5 時間**
            """,
            id="One project, two members.",
        ),
        pytest.param(
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
                        ManHour(name="次郎", hour=1.5),
                    ],
                ),
            ],
            """
            # 工数週次レポート
            
            ## [A001] 開発案件A
            
            - 太郎 さん: 4.0 時間
            - **合計: 4.0 時間**
            
            ## [B001] 開発案件B
            
            - 次郎 さん: 1.5 時間
            - **合計: 1.5 時間**
            """,
            id="Two projects, one member for each.",
        ),
        pytest.param(
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[
                        ManHour(name="太郎", hour=4.0),
                        ManHour(name="次郎", hour=2.5),
                    ],
                ),
                WeeklyProjectReport(
                    project_code="B001",
                    name="開発案件B",
                    man_hours=[
                        ManHour(name="次郎", hour=1.5),
                        ManHour(name="太郎", hour=2.7),
                    ],
                ),
            ],
            """
            # 工数週次レポート
            
            ## [A001] 開発案件A
            
            - 太郎 さん: 4.0 時間
            - 次郎 さん: 2.5 時間
            - **合計: 6.5 時間**
            
            ## [B001] 開発案件B
            
            - 次郎 さん: 1.5 時間
            - 太郎 さん: 2.7 時間
            - **合計: 4.2 時間**
            """,
            id="Two projects, two members for each.",
        ),
        pytest.param(
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
                        ManHour(name="次郎", hour=1.53),
                    ],
                ),
            ],
            """
            # 工数週次レポート
            
            ## [A001] 開発案件A
            
            - 太郎 さん: 4.0 時間
            - **合計: 4.0 時間**
            
            ## [B001] 開発案件B
            
            - 次郎 さん: 1.53 時間
            - **合計: 1.53 時間**
            """,
            id="If with two decimal places, displayed man hour is not rounded.",
        ),
        pytest.param(
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
                        ManHour(name="次郎", hour=1.50),
                    ],
                ),
            ],
            """
            # 工数週次レポート
            
            ## [A001] 開発案件A
            
            - 太郎 さん: 4.0 時間
            - **合計: 4.0 時間**
            
            ## [B001] 開発案件B
            
            - 次郎 さん: 1.5 時間
            - **合計: 1.5 時間**
            """,
            id="If value of two decimal places is zero, it will be omitted.",
        ),
        pytest.param(
            [
                WeeklyProjectReport(
                    project_code="A001",
                    name="開発案件A",
                    man_hours=[
                        ManHour(name="太郎", hour=4.012),
                    ],
                ),
                WeeklyProjectReport(
                    project_code="B001",
                    name="開発案件B",
                    man_hours=[
                        ManHour(name="次郎", hour=1.516),
                    ],
                ),
            ],
            """
            # 工数週次レポート
            
            ## [A001] 開発案件A
            
            - 太郎 さん: 4.01 時間
            - **合計: 4.01 時間**
            
            ## [B001] 開発案件B
            
            - 次郎 さん: 1.52 時間
            - **合計: 1.52 時間**
            """,
            id="If with three decimal places, it will be rounded.",
        ),
    ],
)
def test(reports: list[WeeklyProjectReport], expected: str):
    actual = report_to_msg(reports)
    assert actual == dedent(expected).strip()
