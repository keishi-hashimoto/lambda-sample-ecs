from copy import deepcopy
from dataclasses import dataclass, field
from os import environ
from typing import TypedDict, Final

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
import requests
import polars as pl

logger = Logger()

COL_PROJECT_CODE: Final = "Pコード"
COL_MEMBER_NAME: Final = "名前"
COL_MAN_HOUR: Final = "工数"

ADDITIONAL_CON_PROJECT_NAME: Final = "案件名"
COL_DT: Final = "日付"


class S3ObjectInfo(TypedDict):
    key: str


class S3BucketInfo(TypedDict):
    name: str


class S3Info(TypedDict):
    bucket: S3BucketInfo
    object: S3ObjectInfo


class S3EventRecord(TypedDict):
    s3: S3Info


class S3Event(TypedDict):
    Records: list[S3EventRecord]


class DictFromDf(TypedDict):
    Pコード: str
    案件名: str
    名前: str
    工数: float


@dataclass
class BaseManHour:
    name: str
    hour: float


@dataclass
class ManHour(BaseManHour):
    def __str__(self) -> str:
        return f"{self.name} さん: {self.hour} 時間"


@dataclass
class TotalManHour(BaseManHour):
    name: str = field(default="合計", init=False)

    def __str__(self) -> str:
        return f"**{self.name}: {self.hour} 時間**"


@dataclass
class WeeklyProjectReport:
    project_code: str
    name: str
    man_hours: list[ManHour]

    @property
    def total(self) -> TotalManHour:
        return TotalManHour(sum([m.hour for m in self.man_hours]))

    def __str__(self) -> str:
        return "\n".join(
            [
                f"## [{self.project_code}] {self.name}",
                "",
                *[f"- {m}" for m in self.man_hours],
                f"- {self.total}",
            ]
        )


def read_csv_file(bucket: str, key: str) -> pl.DataFrame:
    try:
        df = pl.read_csv(
            f"s3://{bucket}/{key}", schema_overrides={COL_MAN_HOUR: pl.Float32}
        )
        logger.info(df)
        return df
    except Exception as e:
        logger.error(e)
        raise e


def validate_project_code(df: pl.DataFrame, project_map_df: pl.DataFrame):
    invalid_rows = df.filter(
        pl.col(COL_PROJECT_CODE)
        .is_in(project_map_df[COL_PROJECT_CODE].to_list())
        .not_()
    )

    if not invalid_rows.is_empty():
        msg = "\n".join(
            [
                "以下の P コードは不正です",
                "",
                *[f"* {r[COL_PROJECT_CODE]}" for r in invalid_rows.to_dicts()],
            ]
        )
        logger.error(msg)
        raise ValueError(msg)


def process_df(df: pl.DataFrame) -> pl.DataFrame:
    grouped = df.group_by([COL_PROJECT_CODE, COL_MEMBER_NAME], maintain_order=True)
    with_sum = grouped.sum()
    without_dt = with_sum.select(pl.selectors.exclude(COL_DT))
    logger.info(without_dt)
    return without_dt


def add_project_name_to_df(
    df: pl.DataFrame,
    project_map_df: pl.DataFrame,
) -> pl.DataFrame:
    sql = f"""
        select df.{COL_PROJECT_CODE}, project_map_df.{ADDITIONAL_CON_PROJECT_NAME},
        df.{COL_MEMBER_NAME}, df.{COL_MAN_HOUR}
        from df join project_map_df
        on df.{COL_PROJECT_CODE} = project_map_df.{COL_PROJECT_CODE}
    """
    df_with_project_name = pl.sql(sql).collect()
    logger.info(df_with_project_name)
    return df_with_project_name


def _upsert(
    dict_from_df: DictFromDf, _reports: list[WeeklyProjectReport]
) -> list[WeeklyProjectReport]:
    project_name = dict_from_df[ADDITIONAL_CON_PROJECT_NAME]
    # 副作用回避のために copy する
    reports = deepcopy(_reports)
    target_reports = [p for p in reports if p.name == project_name]
    if not target_reports:
        weekly_report = WeeklyProjectReport(
            project_code=dict_from_df[COL_PROJECT_CODE],
            name=dict_from_df[ADDITIONAL_CON_PROJECT_NAME],
            man_hours=[
                ManHour(
                    name=dict_from_df[COL_MEMBER_NAME], hour=dict_from_df[COL_MAN_HOUR]
                )
            ],
        )
        reports.append(weekly_report)
    else:
        target_report = target_reports[0]
        target_report.man_hours.append(
            ManHour(name=dict_from_df[COL_MEMBER_NAME], hour=dict_from_df[COL_MAN_HOUR])
        )

    return reports


def df_to_project_report(df: pl.DataFrame) -> list[WeeklyProjectReport]:
    dicts_from_df: list[DictFromDf] = df.to_dicts()  # type: ignore [assignment]
    weekly_project_report_list: list[WeeklyProjectReport] = []
    for d in dicts_from_df:
        weekly_project_report_list = _upsert(d, weekly_project_report_list)

    logger.info(weekly_project_report_list)
    return weekly_project_report_list


def report_to_msg(reports: list[WeeklyProjectReport]) -> str:
    return "\n\n".join(["# 工数週次レポート", *[f"{r}" for r in reports]])


def notify_to_slack(msg: str) -> str:
    url = environ["SLACK_URL"]
    try:
        res = requests.post(
            url=url, headers={"Content-Type": "application/json"}, json={"text": msg}
        )
        res.raise_for_status()
        return res.text
    except Exception as e:
        logger.error(f"slack 通知に失敗しました: {e}")
        raise e


@logger.inject_lambda_context(log_event=True)
def handler(event: S3Event, context: LambdaContext):
    logger.info(event)
    logger.info(context)

    # CSV ファイルから工数の生データを読み込み
    s3_info = event["Records"][0]["s3"]
    df = read_csv_file(bucket=s3_info["bucket"]["name"], key=s3_info["object"]["key"])

    project_map_bucket = environ["PROJECT_MAP_BUCKET"]
    project_map_key = environ["PROJECT_MAP_KEY"]
    project_map_df = read_csv_file(bucket=project_map_bucket, key=project_map_key)

    validate_project_code(df, project_map_df)

    processed_df = process_df(df)
    df_with_project_name = add_project_name_to_df(processed_df, project_map_df)

    # TODO: 正規メンバー以外に工数が計上されている場合には警告文を出力する

    reports = df_to_project_report(df_with_project_name)
    msg = report_to_msg(reports)
    notify_to_slack(msg)
    logger.info("Msg has been sent to slack.")
