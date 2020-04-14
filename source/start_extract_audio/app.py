import os
import boto3
from datetime import datetime


mediaconvert_role = os.environ.get(
    "MCROLE",
    "arn:aws:iam::012345678901:role/DummyRole"
)
region = os.environ.get("REGION", "us-east-1")
mediaconvert = boto3.client("mediaconvert", region_name=region)


def lambda_handler(event, context):
    """Start Media Convert job to extract audio Lambda function

    Parameters
    ----------
    event: dict, required
        StepFunctions Input event

    context: object, required
        Lambda Context runtime methods and attributes


    Returns
    ------
    Media Convert job id for audio extract: dict

    """

    try:
        if ("bucket" in event["metadata"] and "key" in event["metadata"]):
            bucket = event["metadata"]["bucket"]
            key = event["metadata"]["key"]
            _id = event["metadata"]["uuid"]
    except KeyError as e:
        return {
            "message": f"Error - {e}"
        }

    payload = {
        "metadata": {
            "status": "IN PROGRESS",
            "uuid": event["metadata"]["uuid"],
            "event_time": event["metadata"]["event_time"],
            "bucket": event["metadata"]["bucket"],
            "key": event["metadata"]["key"],
            "file_name": event["metadata"]["file_name"],
            "execution_arn": event["metadata"]["execution_arn"],
            "start_date": event["metadata"]["start_date"],
            "last_update": ""
        },
        "Output": {}
    }

    file_input = f"s3://{bucket}/{key}"
    destination = f"s3://{bucket}/outputs/{_id}/"

    try:
        response = mediaconvert.describe_endpoints()
    except Exception as e:
        return {
            "message": f"Error - {e}"
        }
    else:
        mediaconvert_endpoint = response["Endpoints"][0]["Url"]
        payload["metadata"]["mediaconvert_endpoint"] = (
            mediaconvert_endpoint
        )
        payload["metadata"]["last_update"] = (
            datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        )
        customer_mediaconvert = boto3.client(
            "mediaconvert",
            region_name=region,
            endpoint_url=mediaconvert_endpoint
        )

    try:
        response = customer_mediaconvert.create_job(
            Role=mediaconvert_role,
            Settings={
              "OutputGroups": [{
                "Name": "File Group",
                "Outputs": [{
                  "ContainerSettings": {
                    "Container": "MP4",
                    "Mp4Settings": {
                      "CslgAtom": "INCLUDE",
                      "FreeSpaceBox": "EXCLUDE",
                      "MoovPlacement": "PROGRESSIVE_DOWNLOAD"
                    }
                  },
                  "AudioDescriptions": [{
                    "AudioTypeControl": "FOLLOW_INPUT",
                    "AudioSourceName": "Audio Selector 1",
                    "CodecSettings": {
                      "Codec": "AAC",
                      "AacSettings": {
                        "AudioDescriptionBroadcasterMix": "NORMAL",
                        "Bitrate": 96000,
                        "RateControlMode": "CBR",
                        "CodecProfile": "LC",
                        "CodingMode": "CODING_MODE_2_0",
                        "RawFormat": "NONE",
                        "SampleRate": 48000,
                        "Specification": "MPEG4"
                      }
                    },
                    "LanguageCodeControl": "FOLLOW_INPUT"
                  }],
                  "Extension": "mp4",
                  "NameModifier": "_audio"
                }],
                "OutputGroupSettings": {
                  "Type": "FILE_GROUP_SETTINGS",
                  "FileGroupSettings": {
                    "Destination": destination
                  }
                }
              }],
              "AdAvailOffset": 0,
              "Inputs": [{
                "AudioSelectors": {
                  "Audio Selector 1": {
                    "Offset": 0,
                    "DefaultSelection": "DEFAULT",
                    "ProgramSelection": 1
                  }
                },
                "VideoSelector": {
                  "ColorSpace": "FOLLOW"
                },
                "FilterEnable": "AUTO",
                "PsiControl": "USE_PSI",
                "FilterStrength": 0,
                "DeblockFilter": "DISABLED",
                "DenoiseFilter": "DISABLED",
                "TimecodeSource": "EMBEDDED",
                "FileInput": file_input
              }]
            }
        )
    except Exception as e:
        return {
            "message": f"Error - {e}"
        }
    else:
        job_id = response['Job']['Id']
        payload["Output"]["Audio"] = {
            "job_id": job_id
        }

    return payload
