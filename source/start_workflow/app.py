import os
import re
import uuid
import boto3
import json

_id = str(uuid.uuid4())
regex = "[^/]+$"

sf_arn = os.environ.get(
    "SF_ARN",
    "arn:aws:states:us-east-1:123456789012:stateMachine:AVOD"
)
region = os.environ.get("REGION", "us-east-1")
aws_environment = os.environ.get("AWSENV", "AWS")

if aws_environment == "AWS_SAM_LOCAL":
    sf = boto3.client(
      "stepfunctions",
      endpoint_url="http://stepfunctions:8083"
    )
else:
    sf = boto3.client(
        "stepfunctions",
        region_name=region
    )


def lambda_handler(event, context):
    """Start StepFunction Lambda function

    Parameters
    ----------
    event: dict, required
        S3 PutObject event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    Object/StepFunction information: dict

    """

    bucket = ""
    key = ""
    file_name = ""
    event_time = ""

    try:
        if ("name" in event["Records"][0]["s3"]["bucket"] and
                "key" in event["Records"][0]["s3"]["object"]):
            bucket = event["Records"][0]["s3"]["bucket"]["name"]
            key = event["Records"][0]["s3"]["object"]["key"]
            file_name = re.findall(regex, key)[0]
            event_time = event["Records"][0]["eventTime"]
    except KeyError as e:
        return {
            "message": f"Error - {e}"
        }

    payload = {
        "metadata": {
            "status": "OK",
            "uuid": _id,
            "event_time": event_time,
            "bucket": bucket,
            "key": key,
            "file_name": file_name
        }
    }

    try:
        response = sf.start_execution(
            stateMachineArn=sf_arn,
            name=f"{file_name}-{_id}",
            input=json.dumps(payload)
        )
    except KeyError as e:
        return {
            "message": f"Error - {e}"
        }

    payload["metadata"]["execution_arn"] = response["executionArn"]
    payload["metadata"]["start_date"] = (
        response["startDate"].strftime("%d-%b-%Y (%H:%M:%S.%f)")
    )

    return payload
