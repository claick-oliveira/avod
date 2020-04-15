import os
import boto3
from datetime import datetime


region = os.environ.get("REGION", "us-east-1")


def lambda_handler(event, context):
    """Get Media Convert job to extract audio Lambda function

    Parameters
    ----------
    event: dict, required
        Start Extract Audio Input event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    Media Convert output for audio extract: dict

    """

    try:
        if (
            "job_id" in event["Output"]["Audio"] and
            "mediaconvert_endpoint" in event["metadata"]
        ):
            job_id = event["Output"]["Audio"]["job_id"]
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
            output_uri = response["Job"]["Settings"]["OutputGroups"][0][
                "OutputGroupSettings"]["FileGroupSettings"]["Destination"]
            extension = response["Job"]["Settings"]["OutputGroups"][0][
                "Outputs"][0]["Extension"]
            modifier = response["Job"]["Settings"]["OutputGroups"][0][
                "Outputs"][0]["NameModifier"]

            bucket = output_uri.split("/")[2]
            folder = "/".join(output_uri.split("/")[3:-1])

            file_name = event["metadata"][
                "file_name"].split("/")[-1].split(".")[0]

            key = folder + "/" + file_name + modifier + "." + extension

            payload["Output"]["Audio"]["bucket"] = bucket
            payload["Output"]["Audio"]["key"] = key

            payload["metadata"]["status"] = "COMPLETE"
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
