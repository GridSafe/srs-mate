import logging

import config


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


def make_rtmp_url(output):
    if not _validate_output(output):
        logging.error("invalid output={}".format(output))
        return None

    target = output["target"]

    rtmp_url = "rtmp://{}/{}/{}".format(
        target["vhost"],
        target["app"],
        target["stream"]
    )

    return rtmp_url


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

    return True


def _validate_inputs(inputs):
    for input1 in inputs:
        if not _validate_input(input1):
            return False

    return True


def _validate_output_target(target):
    for key in ["vhost", "app", "stream"]:
        if key not in target:
            return False

        if not isinstance(target[key], str):
            return False

    return True


def _validate_output(output):
    if "target" not in output:
        return False

    if not isinstance(output["target"], dict):
        return False

    if not _validate_output_target(output["target"]):
        return False

    for key in ["width", "height"]:
        if key not in output:
            return False

        if not isinstance(output[key], int):
            return False

        if output[key] < 0:
            return False

    if "background" in output:
        if not (isinstance(output["background"], str)
                or isinstance(output["background"], int)):
            return False

    return True


def _dump_inputs(inputs, arguments):
    for input1 in inputs:
        arguments.append("-i")
        arguments.append(input1["source"])

    arguments.extend(["-acodec", "aac", "-strict", "-2"]) # workaround


def _dump_background_filters(output, filters):
    filter1 = "nullsrc=size={}x{} [dummy]".format(output["width"], output["height"])
    background = output.get("background", 0)

    if isinstance(background, str):
        template = "movie={}, scale=width={}:height={}"
    else:
        template = "color=color=0x{:06X}:size={}x{}"

    filter2 = template.format(
        background,
        output["width"],
        output["height"]
    )

    filter2 += " [background]"
    filter3 = "[dummy][background] overlay=x=0:y=0 [output0]"
    filters.append(filter1)
    filters.append(filter2)
    filters.append(filter3)


def _dump_scale_filter(index, input1, filters):
    filter1 = "[{}:v] scale=width={}:height={} [input{}]".format(
        index,
        input1["width"],
        input1["height"],
        index
    )

    filters.append(filter1)


def _dump_overlay_filter(index, input1, last_input, filters):
    filter1 = "[output{}][input{}] overlay=x={}:y={}".format(
        index,
        index,
        input1["left"],
        input1["top"]
    )

    if not last_input:
        filter1 += " [output{}]".format(index + 1)

    filters.append(filter1)


def _dump_video_filters(inputs, output, arguments):
    filters = []

    for index, input1 in enumerate(inputs):
        _dump_scale_filter(index, input1, filters)

    _dump_background_filters(output, filters)

    for index, input1 in enumerate(inputs):
        last_input = index + 1 == len(inputs)
        _dump_overlay_filter(index, input1, last_input, filters)

    filters_string = "; ".join(filters)
    arguments.append("-filter_complex")
    arguments.append(filters_string)


def _dump_audio_filters(inputs, arguments):
    filter1 = "amix=inputs={}".format(len(inputs))
    arguments.append("-filter_complex")
    arguments.append(filter1)


def _dump_output(output, arguments):
    target = output["target"]

    rtmp_url = "rtmp://{}:{}/{}?vhost={}/{}".format(
        config.SRS_HOST,
        config.SRS_PORT,
        target["app"],
        target["vhost"],
        target["stream"]
    )

    arguments.append("-f")
    arguments.append("flv")
    arguments.append("-y")
    arguments.append(rtmp_url)
