import subprocess
import logging

import ffmpeg_cmd_line


_processes = {}


def start(inputs, output):
    name = ffmpeg_cmd_line.make_rtmp_url(output)

    if name is None:
        logging.error("failed to make encoder name")
        return False

    if _process_exists(name):
        logging.error("encoder is already running, name={}".format(name))
        return False

    cmd_line_args = ffmpeg_cmd_line.make_arguments(inputs, output)

    if cmd_line_args is None:
        logging.error("failed to make encoder command line argumens, name={}".format(name))
        return False

    if not _create_process(name, cmd_line_args):
        logging.error("failed to start encoder process, cmd_line_args={}".format(cmd_line_args))
        return False

    logging.info("encoder started, name={}".format(name))
    return True


def stop(output):
    name = ffmpeg_cmd_line.make_rtmp_url(output)

    if name is None:
        logging.error("failed to make encoder name")
        return False

    if not _process_exists(name):
        logging.error("encoder is not running, name={}".format(name))
        return False

    _destroy_process(name)
    logging.info("encoder stoped, name={}".format(name))
    return True


def _create_process(name, cmd_line_args):
    try:
        process = subprocess.Popen(
            cmd_line_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
        logging.exception("popen failed")
        return False

    _processes[name] = process
    return True


def _destroy_process(name):
    process = _processes[name]
    del _processes[name]
    process.kill()
    process.wait()


def _process_exists(name):
    return name in _processes
