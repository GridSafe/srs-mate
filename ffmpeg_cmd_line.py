import logging

import config


DEFAULT_INPUT_IS_MUTE = False


def make_arguments(inputs, output):
    if not _validate_inputs(inputs):
        logging.error("invalid inputs={}".format(inputs))
        return None

    if not _validate_output(output):
        logging.error("invalid output={}".format(output))
        return None

    arguments = [config.FFMPEG_PATH]
    _dump_inputs(inputs, arguments)
    _dump_video_filters(inputs, output, arguments)
    _dump_audio_filters(inputs, arguments)
    _dump_output(output, arguments)
    return arguments


def _validate_input(input1):
    if "source" not in input1:
        return False

    if not isinstance(input1["source"], str):
        return False

    for key in ["left", "top", "width", "height"]:
        if key not in input1:
            return False

        if not isinstance(input1[key], int):
            return False

        if input1[key] < 0:
            return False

    if not isinstance(input1.get("is_mute", DEFAULT_INPUT_IS_MUTE), bool):
        return False

    return True


def _validate_inputs(inputs):
    for input1 in inputs:
        if not _validate_input(input1):
            return False

    return True


def _validate_output_target(target):
    for key in ["host", "app", "stream"]:
        if key not in target:
            return False

        if not isinstance(target[key], str):
            return False

    return True


def _validate_output(output):
    if "targets" not in output:
        return False

    if not isinstance(output["targets"], list):
        return False

    if len(output["targets"]) == 0:
        return False

    for target in output["targets"]:
        if not isinstance(target, dict):
            return False

        if not _validate_output_target(target):
            return False

    for key in ["width", "height"]:
        if key not in output:
            return False

        if not isinstance(output[key], int):
            return False

        if output[key] < 0:
            return False

    for key in ["video_bitrate", "audio_bitrate"]:
        if key in output:
            if not isinstance(output[key], int):
                return False

            if output[key] < 0:
                return False

    if "background_color" in output:
        if not isinstance(output["background_color"], int):
            return False

        if output["background_color"] < 0 or output["background_color"] > 0xFFFFFF:
            return False

    return True


def _dump_inputs(inputs, arguments):
    for input1 in inputs:
        if input1.get("is_mute", DEFAULT_INPUT_IS_MUTE):
            continue

        arguments.append("-i")
        arguments.append(input1["source"])


def _dump_background_filter(output, filters):
    if "background_color" in output:
        filter1 = "color=color=0x{:06X}:size={}x{} [out0]".format(
            output["background_color"],
            output["width"],
            output["height"]
        )
    else:
        filter1 = "nullsrc=size={}x{} [out0]".format(output["width"], output["height"])

    filters.append(filter1)


def _dump_scale_filter(index, input1, mute_input_count, filters):
    if input1.get("is_mute", DEFAULT_INPUT_IS_MUTE):
        filter1 = "movie='{}', scale=width={}:height={} [in{}]".format(
            input1["source"].replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:"),
            input1["width"],
            input1["height"],
            index
        )
    else:
        filter1 = "[{}:v] scale=width={}:height={} [in{}]".format(
            index - mute_input_count,
            input1["width"],
            input1["height"],
            index
        )

    filters.append(filter1)


def _dump_overlay_filter(index, input1, is_last_input, filters):
    filter1 = "[out{}][in{}] overlay=x={}:y={}".format(
        index,
        index,
        input1["left"],
        input1["top"]
    )

    if not is_last_input:
        filter1 += " [out{}]".format(index + 1)

    filters.append(filter1)


def _dump_video_filters(inputs, output, arguments):
    filters = []
    mute_input_count = 0

    for index, input1 in enumerate(inputs):
        _dump_scale_filter(index, input1, mute_input_count, filters)

        if input1.get("is_mute", DEFAULT_INPUT_IS_MUTE):
            mute_input_count += 1

    _dump_background_filter(output, filters)

    for index, input1 in enumerate(inputs):
        is_last_input = index + 1 == len(inputs)
        _dump_overlay_filter(index, input1, is_last_input, filters)

    filters_string = "; ".join(filters)
    arguments.append("-filter_complex")
    arguments.append(filters_string)


def _dump_audio_filters(inputs, arguments):
    n = 0

    for input1 in inputs:
        if input1.get("is_mute", DEFAULT_INPUT_IS_MUTE):
            continue

        n += 1

    if n == 0:
        return

    filter1 = "amix=inputs={}".format(n)
    arguments.append("-filter_complex")
    arguments.append(filter1)


def _dump_output(output, arguments):
    arguments.extend([
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-strict",
        "experimental",
    ])

    if "video_bitrate" in output:
        arguments.append("-b:v")
        arguments.append("{}k".format(output["video_bitrate"]))

    if "audio_bitrate" in output:
        arguments.append("-b:a")
        arguments.append("{}k".format(output["audio_bitrate"]))

    rtmp_urls = []

    for target in output["targets"]:
        rtmp_url = _make_rtmp_url(target)
        rtmp_urls.append(rtmp_url)

    arguments.append("-f")
    arguments.append("flv")
    arguments.append("tee:" + "|".join(list(rtmp_urls)))


def _make_rtmp_url(target):
    rtmp_url = "rtmp://{}/{}/{}".format(
        target["host"],
        target["app"],
        target["stream"]
    )

    return rtmp_url
