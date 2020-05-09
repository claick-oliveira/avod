import os
import boto3
from datetime import datetime


region = os.environ.get("REGION", "us-east-1")


def lambda_handler(event, context):
    """Start HSL job function

    Parameters
    ----------
    event: dict, required
        StepFunctions Input event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    Media Convert HLS job id: dict

    """

    try:
        if (
            "job_id" in event["Outputs"]["HLS"] and
            "mediaconvert_endpoint" in event["metadata"]
        ):
            job_id = event["Outputs"]["HLS"]["job_id"]
            mediaconvert_endpoint = event["metadata"]["mediaconvert_endpoint"]
            mediaconvert = boto3.client(
                "mediaconvert",
                region_name=region,
                endpoint_url=mediaconvert_endpoint
            )
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    payload = event

    try:
        response = mediaconvert.get_job(Id=job_id)
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }
    else:
        if (
            response["Job"]["Status"] == 'IN_PROGRESS' or
            response["Job"]["Status"] == 'PROGRESSING'
        ):
            payload["metadata"]["status"] = "IN PROGRESS"
            payload["metadata"]["last_update"] = (
                datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            )
        elif response["Job"]["Status"] == 'COMPLETE':
            payload["metadata"]["status"] = "COMPLETED"
            payload["metadata"]["last_update"] = (
                datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            )
        else:
            raise {
                "message": (
                    f"Error to get status from mediaconvert: {response}"
                )
            }

    return payload
