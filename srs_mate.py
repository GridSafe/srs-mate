from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import logging.config

import config
import encoder_mgr


_outputs = {}
_last_output_id = -1


class _CommandHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/command":
            self.send_response(404)
            self.end_headers()
            return

        try:
            command = json.loads(self.rfile.read(int(self.headers["Content-Length"]))
                                 .decode("utf-8"))
            result = json.dumps(_handle_command(command)).encode("utf-8")
        except:
            logging.exception("uncaught exception")
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(result)


def _validate_command(command):
    if "action" not in command:
        return False

    if command["action"] != "start" and command["action"] != "stop" \
       and command["action"] != "restart":
        return False

    if command["action"] == "start" or command["action"] == "restart":
        if "inputs" not in command:
            return False

        if not isinstance(command["inputs"], list):
            return False

        if "output" not in command:
            return False

        if not isinstance(command["output"], dict):
            return False

    if command["action"] == "stop" or command["action"] == "restart":
        if "output_id" not in command:
            return False

        if not isinstance(command["output_id"], int):
            return False

    return True


def _handle_command(command):
    result = {"success": False}

    if not _validate_command(command):
        logging.error("invalid command={}".format(command))
        return result

    if command["action"] in ["stop", "restart"]:
        output = _get_output(command["output_id"])

        if output is None:
            logging.error("invalid output_id={}".format(command["output_id"]))
            return result

        _delete_output(command["output_id"])

        if not encoder_mgr.stop(output):
            logging.error("failed to stop encoder")
            return result

    if command["action"] in ["start", "restart"]:
        if not encoder_mgr.start(command["inputs"], command["output"]):
            logging.error("failed to start encoder")
            return result

        result["output_id"] = _add_output(command["output"])

    result["success"] = True
    return result


def _get_next_output_id():
    output_id = (_last_output_id + 1) % config.MAX_NUMBER_OF_OUTPUT

    for _ in range(config.MAX_NUMBER_OF_OUTPUT):
        if output_id not in _outputs:
            break

        output_id = (output_id + 1) % config.MAX_NUMBER_OF_OUTPUT

    if output_id in _outputs:
        output = _outputs[output_id]
        del _outputs[output_id]

        if not encoder_mgr.stop(output):
            logging.error("failed to stop encoder")
            return result

    _last_output_id = output_id
    return output_id


def _add_output(output):
    output_id = _get_next_output_id()
    _outputs[output_id] = output
    return output_id


def _delete_output(output_id):
    del _outputs[output_id]


def _get_output(output_id):
    return _outputs.get(output_id)


if __name__ == "__main__":
    logging.config.dictConfig(config.LOGGING)
    http_server = HTTPServer((config.LISTEN_HOST, config.LISTEN_PORT), _CommandHandler)
    http_server.serve_forever()
