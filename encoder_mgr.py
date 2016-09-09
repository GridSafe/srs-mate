import logging
import shlex
import subprocess

import config
import ffmpeg_cmd_line


_last_vpid = -1
_vpid_to_proc = {}


def start(inputs, output):
    cmd_line_args = ffmpeg_cmd_line.make_arguments(inputs, output)

    if cmd_line_args is None:
        logging.error("failed to make encoder command line argumens, inputs={}, output={}"
                      .format(inputs, output))
        return False

    proc = _create_process(cmd_line_args)

    if proc is None:
        logging.error("failed to start encoder process, cmd_line_args={}".format(cmd_line_args))
        return False

    vpid = _get_next_vpid()
    _vpid_to_proc[vpid] = proc
    logging.info("encoder started, inputs={}, output={}, vpid={}".format(inputs, output, vpid))
    return vpid


def stop(vpid):
    proc = _vpid_to_proc.get(vpid)

    if proc is None:
        logging.error("bad vpid={}".format(vpid))
        return False

    _destroy_process(proc)
    del _vpid_to_proc[vpid]
    logging.info("encoder stoped, vpid={}".format(vpid))
    return True


def _create_process(cmd_line_args):
    cmd_line = " ".join(map(shlex.quote, cmd_line_args))

    try:
        proc = subprocess.Popen(
            cmd_line_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        logging.info("create process: cmd_line={}".format(cmd_line))
    except:
        logging.exception("create process failed, cmd_line={}".format(cmd_line))
        return None

    return proc


def _destroy_process(proc):
    proc.kill()
    proc.wait()


def _get_next_vpid():
    global _last_vpid
    vpid = (_last_vpid + 1) % config.MAX_NUMBER_OF_ENCODERS

    for _ in range(config.MAX_NUMBER_OF_ENCODERS):
        if vpid not in _vpid_to_proc:
            break

        vpid = (vpid + 1) % config.MAX_NUMBER_OF_ENCODERS

    if vpid in _vpid_to_proc:
        stop(vpid)

    _last_vpid = vpid
    return vpid
