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
            "bucket" in event["metadata"] and
            "key" in event["metadata"] and
            "bucket" in event["Outputs"]["SRT"] and
            "key" in event["Outputs"]["SRT"]
        ):
            bucket = event["metadata"]["bucket"]
            key_video = event["metadata"]["key"]
            file_name = event["metadata"]["file_name"]
            key_srt = event["Outputs"]["SRT"]["key"]
            _id = event["metadata"]["uuid"]
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }

    payload = event
    payload["metadata"]["status"] = "IN PROGRESS"
    hls_name = file_name.split('.')[0]+'.m3u8'
    file_input = f"s3://{bucket}/{key_video}"
    destination = f"s3://{bucket}/outputs/{_id}/HLS/"
    caption_input = f"s3://{bucket}/{key_srt}"

    try:
        response = mediaconvert.describe_endpoints()
    except KeyError as e:
        raise {
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
              "OutputGroups": [
                {
                  "CustomName": "HLS",
                  "Name": "Apple HLS",
                  "Outputs": [
                    {
                      "ContainerSettings": {
                        "Container": "M3U8",
                        "M3u8Settings": {
                          "AudioFramesPerPes": 4,
                          "PcrControl": "PCR_EVERY_PES_PACKET",
                          "PmtPid": 480,
                          "PrivateMetadataPid": 503,
                          "ProgramNumber": 1,
                          "PatInterval": 0,
                          "PmtInterval": 0,
                          "Scte35Source": "NONE",
                          "VideoPid": 481,
                          "AudioPids": [
                            482,
                            483,
                            484,
                            485,
                            486,
                            487,
                            488,
                            489,
                            490,
                            491,
                            492,
                            493,
                            494,
                            495,
                            496,
                            497,
                            498
                          ]
                        }
                      },
                      "VideoDescription": {
                        "Width": 1920,
                        "ScalingBehavior": "DEFAULT",
                        "Height": 1080,
                        "VideoPreprocessors": {
                          "Deinterlacer": {
                            "Algorithm": "INTERPOLATE",
                            "Mode": "DEINTERLACE",
                            "Control": "NORMAL"
                          }
                        },
                        "TimecodeInsertion": "DISABLED",
                        "AntiAlias": "ENABLED",
                        "Sharpness": 50,
                        "CodecSettings": {
                          "Codec": "H_264",
                          "H264Settings": {
                            "InterlaceMode": "PROGRESSIVE",
                            "ParNumerator": 1,
                            "NumberReferenceFrames": 3,
                            "Syntax": "DEFAULT",
                            "FramerateDenominator": 1001,
                            "GopClosedCadence": 1,
                            "HrdBufferInitialFillPercentage": 90,
                            "GopSize": 90,
                            "Slices": 1,
                            "GopBReference": "DISABLED",
                            "HrdBufferSize": 17000000,
                            "MaxBitrate": 6000000,
                            "SlowPal": "DISABLED",
                            "ParDenominator": 1,
                            "SpatialAdaptiveQuantization": "ENABLED",
                            "TemporalAdaptiveQuantization": "ENABLED",
                            "FlickerAdaptiveQuantization": "ENABLED",
                            "EntropyEncoding": "CABAC",
                            "FramerateControl": "SPECIFIED",
                            "RateControlMode": "QVBR",
                            "QvbrSettings": {
                              "QvbrQualityLevel": 9,
                              "QvbrQualityLevelFineTune": 0
                            },
                            "CodecProfile": "HIGH",
                            "Telecine": "NONE",
                            "FramerateNumerator": 30000,
                            "MinIInterval": 0,
                            "AdaptiveQuantization": "HIGH",
                            "CodecLevel": "LEVEL_4",
                            "FieldEncoding": "PAFF",
                            "SceneChangeDetect": "ENABLED",
                            "QualityTuningLevel": "MULTI_PASS_HQ",
                            "FramerateConversionAlgorithm": "DUPLICATE_DROP",
                            "UnregisteredSeiTimecode": "DISABLED",
                            "GopSizeUnits": "FRAMES",
                            "ParControl": "SPECIFIED",
                            "NumberBFramesBetweenReferenceFrames": 1,
                            "RepeatPps": "DISABLED"
                          }
                        },
                        "AfdSignaling": "NONE",
                        "DropFrameTimecode": "ENABLED",
                        "RespondToAfd": "NONE",
                        "ColorMetadata": "INSERT"
                      },
                      "AudioDescriptions": [
                        {
                          "AudioTypeControl": "FOLLOW_INPUT",
                          "AudioSourceName": "Audio Selector 1",
                          "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {
                              "AudioDescriptionBroadcasterMix": "NORMAL",
                              "Bitrate": 128000,
                              "RateControlMode": "CBR",
                              "CodecProfile": "LC",
                              "CodingMode": "CODING_MODE_2_0",
                              "RawFormat": "NONE",
                              "SampleRate": 48000,
                              "Specification": "MPEG4"
                            }
                          },
                          "LanguageCodeControl": "FOLLOW_INPUT",
                          "AudioType": 0
                        }
                      ],
                      "OutputSettings": {
                        "HlsSettings": {
                          "SegmentModifier": "$dt$"
                        }
                      },
                      "NameModifier": "_1080"
                    },
                    {
                      "ContainerSettings": {
                        "Container": "M3U8",
                        "M3u8Settings": {
                          "AudioFramesPerPes": 4,
                          "PcrControl": "PCR_EVERY_PES_PACKET",
                          "PmtPid": 480,
                          "PrivateMetadataPid": 503,
                          "ProgramNumber": 1,
                          "PatInterval": 0,
                          "PmtInterval": 0,
                          "Scte35Source": "NONE",
                          "VideoPid": 481,
                          "AudioPids": [
                            482,
                            483,
                            484,
                            485,
                            486,
                            487,
                            488,
                            489,
                            490,
                            491,
                            492,
                            493,
                            494,
                            495,
                            496,
                            497,
                            498
                          ]
                        }
                      },
                      "VideoDescription": {
                        "Width": 1280,
                        "ScalingBehavior": "DEFAULT",
                        "Height": 720,
                        "VideoPreprocessors": {
                          "Deinterlacer": {
                            "Algorithm": "INTERPOLATE",
                            "Mode": "DEINTERLACE",
                            "Control": "NORMAL"
                          }
                        },
                        "TimecodeInsertion": "DISABLED",
                        "AntiAlias": "ENABLED",
                        "Sharpness": 50,
                        "CodecSettings": {
                          "Codec": "H_264",
                          "H264Settings": {
                            "InterlaceMode": "PROGRESSIVE",
                            "ParNumerator": 1,
                            "NumberReferenceFrames": 3,
                            "Syntax": "DEFAULT",
                            "FramerateDenominator": 1001,
                            "GopClosedCadence": 1,
                            "HrdBufferInitialFillPercentage": 90,
                            "GopSize": 90,
                            "Slices": 1,
                            "GopBReference": "ENABLED",
                            "HrdBufferSize": 7000000,
                            "MaxBitrate": 2000000,
                            "SlowPal": "DISABLED",
                            "ParDenominator": 1,
                            "SpatialAdaptiveQuantization": "ENABLED",
                            "TemporalAdaptiveQuantization": "ENABLED",
                            "FlickerAdaptiveQuantization": "ENABLED",
                            "EntropyEncoding": "CABAC",
                            "FramerateControl": "SPECIFIED",
                            "RateControlMode": "QVBR",
                            "QvbrSettings": {
                              "QvbrQualityLevel": 7,
                              "QvbrQualityLevelFineTune": 0
                            },
                            "CodecProfile": "HIGH",
                            "Telecine": "NONE",
                            "FramerateNumerator": 30000,
                            "MinIInterval": 0,
                            "AdaptiveQuantization": "HIGH",
                            "CodecLevel": "LEVEL_4",
                            "FieldEncoding": "PAFF",
                            "SceneChangeDetect": "ENABLED",
                            "QualityTuningLevel": "MULTI_PASS_HQ",
                            "FramerateConversionAlgorithm": "DUPLICATE_DROP",
                            "UnregisteredSeiTimecode": "DISABLED",
                            "GopSizeUnits": "FRAMES",
                            "ParControl": "SPECIFIED",
                            "NumberBFramesBetweenReferenceFrames": 3,
                            "RepeatPps": "DISABLED"
                          }
                        },
                        "AfdSignaling": "NONE",
                        "DropFrameTimecode": "ENABLED",
                        "RespondToAfd": "NONE",
                        "ColorMetadata": "INSERT"
                      },
                      "AudioDescriptions": [
                        {
                          "AudioTypeControl": "FOLLOW_INPUT",
                          "AudioSourceName": "Audio Selector 1",
                          "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {
                              "AudioDescriptionBroadcasterMix": "NORMAL",
                              "Bitrate": 96000,
                              "RateControlMode": "CBR",
                              "CodecProfile": "HEV1",
                              "CodingMode": "CODING_MODE_2_0",
                              "RawFormat": "NONE",
                              "SampleRate": 48000,
                              "Specification": "MPEG4"
                            }
                          },
                          "LanguageCodeControl": "FOLLOW_INPUT",
                          "AudioType": 0
                        }
                      ],
                      "OutputSettings": {
                        "HlsSettings": {
                          "SegmentModifier": "$dt$"
                        }
                      },
                      "NameModifier": "_720"
                    },
                    {
                      "ContainerSettings": {
                        "Container": "M3U8",
                        "M3u8Settings": {
                          "AudioFramesPerPes": 4,
                          "PcrControl": "PCR_EVERY_PES_PACKET",
                          "PmtPid": 480,
                          "PrivateMetadataPid": 503,
                          "ProgramNumber": 1,
                          "PatInterval": 0,
                          "PmtInterval": 0,
                          "Scte35Source": "NONE",
                          "VideoPid": 481,
                          "AudioPids": [
                            482,
                            483,
                            484,
                            485,
                            486,
                            487,
                            488,
                            489,
                            490,
                            491,
                            492,
                            493,
                            494,
                            495,
                            496,
                            497,
                            498
                          ]
                        }
                      },
                      "VideoDescription": {
                        "Width": 640,
                        "ScalingBehavior": "DEFAULT",
                        "Height": 480,
                        "VideoPreprocessors": {
                          "Deinterlacer": {
                            "Algorithm": "INTERPOLATE",
                            "Mode": "DEINTERLACE",
                            "Control": "NORMAL"
                          }
                        },
                        "TimecodeInsertion": "DISABLED",
                        "AntiAlias": "ENABLED",
                        "Sharpness": 50,
                        "CodecSettings": {
                          "Codec": "H_264",
                          "H264Settings": {
                            "InterlaceMode": "PROGRESSIVE",
                            "ParNumerator": 1,
                            "NumberReferenceFrames": 3,
                            "Syntax": "DEFAULT",
                            "FramerateDenominator": 1001,
                            "GopClosedCadence": 1,
                            "HrdBufferInitialFillPercentage": 90,
                            "GopSize": 90,
                            "Slices": 1,
                            "GopBReference": "ENABLED",
                            "HrdBufferSize": 1200000,
                            "MaxBitrate": 1000000,
                            "SlowPal": "DISABLED",
                            "ParDenominator": 1,
                            "SpatialAdaptiveQuantization": "ENABLED",
                            "TemporalAdaptiveQuantization": "ENABLED",
                            "FlickerAdaptiveQuantization": "ENABLED",
                            "EntropyEncoding": "CABAC",
                            "FramerateControl": "SPECIFIED",
                            "RateControlMode": "QVBR",
                            "QvbrSettings": {
                              "QvbrQualityLevel": 7,
                              "QvbrQualityLevelFineTune": 0
                            },
                            "CodecProfile": "MAIN",
                            "Telecine": "NONE",
                            "FramerateNumerator": 30000,
                            "MinIInterval": 0,
                            "AdaptiveQuantization": "HIGH",
                            "CodecLevel": "LEVEL_3_1",
                            "FieldEncoding": "PAFF",
                            "SceneChangeDetect": "ENABLED",
                            "QualityTuningLevel": "MULTI_PASS_HQ",
                            "FramerateConversionAlgorithm": "DUPLICATE_DROP",
                            "UnregisteredSeiTimecode": "DISABLED",
                            "GopSizeUnits": "FRAMES",
                            "ParControl": "SPECIFIED",
                            "NumberBFramesBetweenReferenceFrames": 3,
                            "RepeatPps": "DISABLED"
                          }
                        },
                        "AfdSignaling": "NONE",
                        "DropFrameTimecode": "ENABLED",
                        "RespondToAfd": "NONE",
                        "ColorMetadata": "INSERT"
                      },
                      "AudioDescriptions": [
                        {
                          "AudioTypeControl": "FOLLOW_INPUT",
                          "AudioSourceName": "Audio Selector 1",
                          "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {
                              "AudioDescriptionBroadcasterMix": "NORMAL",
                              "Bitrate": 64000,
                              "RateControlMode": "CBR",
                              "CodecProfile": "HEV1",
                              "CodingMode": "CODING_MODE_2_0",
                              "RawFormat": "NONE",
                              "SampleRate": 48000,
                              "Specification": "MPEG4"
                            }
                          },
                          "LanguageCodeControl": "FOLLOW_INPUT",
                          "AudioType": 0
                        }
                      ],
                      "OutputSettings": {
                        "HlsSettings": {
                          "SegmentModifier": "$dt$"
                        }
                      },
                      "NameModifier": "_480"
                    },
                    {
                      "ContainerSettings": {
                        "Container": "M3U8",
                        "M3u8Settings": {
                          "AudioFramesPerPes": 4,
                          "PcrControl": "PCR_EVERY_PES_PACKET",
                          "PmtPid": 480,
                          "PrivateMetadataPid": 503,
                          "ProgramNumber": 1,
                          "PatInterval": 0,
                          "PmtInterval": 0,
                          "Scte35Source": "NONE",
                          "VideoPid": 481,
                          "AudioPids": [
                            482,
                            483,
                            484,
                            485,
                            486,
                            487,
                            488,
                            489,
                            490,
                            491,
                            492,
                            493,
                            494,
                            495,
                            496,
                            497,
                            498
                          ]
                        }
                      },
                      "VideoDescription": {
                        "Width": 640,
                        "ScalingBehavior": "DEFAULT",
                        "Height": 360,
                        "VideoPreprocessors": {
                          "Deinterlacer": {
                            "Algorithm": "INTERPOLATE",
                            "Mode": "DEINTERLACE",
                            "Control": "NORMAL"
                          }
                        },
                        "TimecodeInsertion": "DISABLED",
                        "AntiAlias": "ENABLED",
                        "Sharpness": 50,
                        "CodecSettings": {
                          "Codec": "H_264",
                          "H264Settings": {
                            "InterlaceMode": "PROGRESSIVE",
                            "ParNumerator": 1,
                            "NumberReferenceFrames": 3,
                            "Syntax": "DEFAULT",
                            "FramerateDenominator": 1001,
                            "GopClosedCadence": 1,
                            "HrdBufferInitialFillPercentage": 90,
                            "GopSize": 90,
                            "Slices": 1,
                            "GopBReference": "ENABLED",
                            "HrdBufferSize": 1200000,
                            "MaxBitrate": 700000,
                            "SlowPal": "DISABLED",
                            "ParDenominator": 1,
                            "SpatialAdaptiveQuantization": "ENABLED",
                            "TemporalAdaptiveQuantization": "ENABLED",
                            "FlickerAdaptiveQuantization": "ENABLED",
                            "EntropyEncoding": "CABAC",
                            "FramerateControl": "SPECIFIED",
                            "RateControlMode": "QVBR",
                            "QvbrSettings": {
                              "QvbrQualityLevel": 7,
                              "QvbrQualityLevelFineTune": 0
                            },
                            "CodecProfile": "MAIN",
                            "Telecine": "NONE",
                            "FramerateNumerator": 30000,
                            "MinIInterval": 0,
                            "AdaptiveQuantization": "MEDIUM",
                            "CodecLevel": "LEVEL_3_1",
                            "FieldEncoding": "PAFF",
                            "SceneChangeDetect": "ENABLED",
                            "QualityTuningLevel": "MULTI_PASS_HQ",
                            "FramerateConversionAlgorithm": "DUPLICATE_DROP",
                            "UnregisteredSeiTimecode": "DISABLED",
                            "GopSizeUnits": "FRAMES",
                            "ParControl": "SPECIFIED",
                            "NumberBFramesBetweenReferenceFrames": 3,
                            "RepeatPps": "DISABLED"
                          }
                        },
                        "AfdSignaling": "NONE",
                        "DropFrameTimecode": "ENABLED",
                        "RespondToAfd": "NONE",
                        "ColorMetadata": "INSERT"
                      },
                      "AudioDescriptions": [
                        {
                          "AudioTypeControl": "FOLLOW_INPUT",
                          "AudioSourceName": "Audio Selector 1",
                          "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {
                              "AudioDescriptionBroadcasterMix": "NORMAL",
                              "Bitrate": 64000,
                              "RateControlMode": "CBR",
                              "CodecProfile": "HEV1",
                              "CodingMode": "CODING_MODE_2_0",
                              "RawFormat": "NONE",
                              "SampleRate": 48000,
                              "Specification": "MPEG4"
                            }
                          },
                          "LanguageCodeControl": "FOLLOW_INPUT",
                          "AudioType": 0
                        }
                      ],
                      "OutputSettings": {
                        "HlsSettings": {
                          "SegmentModifier": "$dt$"
                        }
                      },
                      "NameModifier": "_360"
                    },
                    {
                      "ContainerSettings": {
                        "Container": "M3U8",
                        "M3u8Settings": {
                          "AudioFramesPerPes": 4,
                          "PcrControl": "PCR_EVERY_PES_PACKET",
                          "PmtPid": 480,
                          "PrivateMetadataPid": 503,
                          "ProgramNumber": 1,
                          "PatInterval": 0,
                          "PmtInterval": 0,
                          "Scte35Source": "NONE",
                          "NielsenId3": "NONE",
                          "TimedMetadata": "NONE",
                          "VideoPid": 481,
                          "AudioPids": [
                            482,
                            483,
                            484,
                            485,
                            486,
                            487,
                            488,
                            489,
                            490,
                            491,
                            492
                          ]
                        }
                      },
                      "OutputSettings": {
                        "HlsSettings": {
                          "AudioGroupId": "program_audio",
                          "AudioOnlyContainer": "AUTOMATIC",
                          "IFrameOnlyManifest": "EXCLUDE"
                        }
                      },
                      "NameModifier": "WebVTT",
                      "CaptionDescriptions": [
                        {
                          "CaptionSelectorName": "Captions Selector 1",
                          "DestinationSettings": {
                            "DestinationType": "WEBVTT"
                          },
                          "LanguageCode": "POR"
                        }
                      ]
                    }
                  ],
                  "OutputGroupSettings": {
                    "Type": "HLS_GROUP_SETTINGS",
                    "HlsGroupSettings": {
                      "ManifestDurationFormat": "INTEGER",
                      "SegmentLength": 10,
                      "TimedMetadataId3Period": 10,
                      "CaptionLanguageSetting": "OMIT",
                      "Destination": destination,
                      "TimedMetadataId3Frame": "PRIV",
                      "CodecSpecification": "RFC_4281",
                      "OutputSelection": "MANIFESTS_AND_SEGMENTS",
                      "ProgramDateTimePeriod": 600,
                      "MinSegmentLength": 0,
                      "MinFinalSegmentLength": 0,
                      "DirectoryStructure": "SINGLE_DIRECTORY",
                      "ProgramDateTime": "EXCLUDE",
                      "SegmentControl": "SEGMENTED_FILES",
                      "ManifestCompression": "NONE",
                      "ClientCache": "ENABLED",
                      "StreamInfResolution": "INCLUDE"
                    }
                  }
                }
              ],
              "AdAvailOffset": 0,
              "Inputs": [
                {
                  "AudioSelectors": {
                    "Audio Selector 1": {
                      "Offset": 0,
                      "DefaultSelection": "DEFAULT",
                      "ProgramSelection": 1
                    }
                  },
                  "VideoSelector": {
                    "ColorSpace": "FOLLOW",
                    "Rotate": "DEGREE_0",
                    "AlphaBehavior": "DISCARD"
                  },
                  "FilterEnable": "AUTO",
                  "PsiControl": "USE_PSI",
                  "FilterStrength": 0,
                  "DeblockFilter": "DISABLED",
                  "DenoiseFilter": "DISABLED",
                  "TimecodeSource": "EMBEDDED",
                  "CaptionSelectors": {
                    "Captions Selector 1": {
                      "SourceSettings": {
                        "SourceType": "SRT",
                        "FileSourceSettings": {
                          "SourceFile": caption_input
                        }
                      }
                    }
                  },
                  "FileInput": file_input
                }
              ]
            }
          )
    except KeyError as e:
        raise {
            "message": f"Error - {e}"
        }
    else:
        job_id = response['Job']['Id']
        payload["Outputs"]["HLS"] = {
            "job_id": job_id,
            "bucket": bucket,
            "key": f"{destination}{hls_name}"
        }

    return payload
