import pytest
from textwrap import dedent
import sys

sys.path.append("..")
from lambda_function import report_to_msg, WeeklyProjectReport, ManHour
import polars as pl

from typing import TypeAlias

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
    ],
)
def test(reports: list[WeeklyProjectReport], expected: str):
    actual = report_to_msg(reports)
    assert actual == dedent(expected).strip()
