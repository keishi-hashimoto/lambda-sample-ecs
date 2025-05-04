from aws_lambda_powertools.utilities.typing import LambdaContext


def handler(event, context: LambdaContext):
    print(f"{event=}")
    print(f"{context=}")
