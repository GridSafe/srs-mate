import subprocess

import ffmpeg_cmd_line


_processes = {}


def start(inputs, output):
    name = ffmpeg_cmd_line.make_rtmp_url(output)

    if name is None:
        logging.error("failed to make encoder name")
        return False

    if _process_exists(name):
        _destroy_process(name)

    cmd_line_args = ffmpeg_cmd_line.make_arguments(inputs, output)

    if cmd_line_args is None:
        logging.error("failed to make encoder command line argumens")
        return False

    if not _create_process(name, cmd_line_args):
        logging.error("failed to start encoder process")
        return False

    return True


def stop(output):
    name = ffmpeg_cmd_line.make_rtmp_url(output)

    if name is None:
        logging.error("failed to make encoder name")
        return False

    if _process_exists(name):
        _destroy_process(name)

    return True


def _create_process(name, cmd_line_args):
    try:
        process = subprocess.Popen(
            cmd_line_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except:
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
