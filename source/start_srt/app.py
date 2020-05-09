import os
import boto3
import math
import ast
from datetime import datetime


target_language_code = os.environ.get("TARGETLANGCODE", "pt-BR")
region = os.environ.get("REGION", "us-east-1")
s3 = boto3.client("s3", region_name=region)


# Format an SRT timestamp in HH:MM:SS,mmm
def format_SRT(time_seconds):

    ONE_HOUR = 60 * 60
    ONE_MINUTE = 60
    hours = math.floor(time_seconds / ONE_HOUR)
    remainder = time_seconds - (hours * ONE_HOUR)
    minutes = math.floor(remainder / 60)
    remainder = remainder - (minutes * ONE_MINUTE)
    seconds = math.floor(remainder)
    remainder = remainder - seconds
    millis = remainder

    return (
        str(hours).zfill(2) + ":" +
        str(minutes).zfill(2) + ":" +
        str(seconds).zfill(2) + "," +
        str(math.floor(millis * 1000)).zfill(3)
    )


def lambda_handler(event, context):
    """Start SRT job to generate captions from Web Captions function

    Parameters
    ----------
    event: dict, required
        StepFunctions Input event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    SRT file path: dict

    """

    try:
        if ("WebCaptions" in event["Outputs"]):
            bucket = event["Outputs"]["WebCaptions"]["bucket"]
            key = event["Outputs"]["WebCaptions"]["key"]
            _id = event["metadata"]["uuid"]
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    payload = event

    try:
        transcribe_file = s3.get_object(Bucket=bucket, Key=key)
        captions = ast.literal_eval(
            transcribe_file["Body"].read().decode("utf-8")
        )
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    srt = ''
    index = 1

    for caption in captions:
        srt += f"{str(index)}\n"
        srt += (
            format_SRT(float(caption['start'])) + " --> " +
            format_SRT(float(caption['end'])) + "\n"
        )
        srt += caption["caption"] + '\n\n'
        index += 1

    srt_name = f"Captions_{target_language_code}.srt"
    destination_key = f"outputs/{_id}/{srt_name}"

    temp_file = f"/tmp/{srt_name}"
    os.mknod(temp_file)

    with open(temp_file, "w") as f:
        print(srt, file=f)

    try:
        s3.upload_file(temp_file, bucket, destination_key)

        payload["metadata"]["status"] = "COMPLETED"
        payload["metadata"]["last_update"] = (
            datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        )
        payload["Outputs"]["SRT"] = {
            "bucket": bucket,
            "key": f"{destination_key}"
        }
        return payload
    except KeyError as e:
        payload["metadata"]["status"] = "FAILED"
        payload["metadata"]["last_update"] = (
            datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        )
        payload["Outputs"]["SRT"] = {
            "message": f"{e}"
        }
        raise payload
