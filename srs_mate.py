from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import logging.config

import config
import encoder_mgr


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

    return True


def _handle_command(command):
    if not _validate_command(command):
        logging.error("invalid command={}".format(command))
        return {"success": False}

    if command["action"] in ["restart", "stop"]:
        if not encoder_mgr.stop(command["output"]):
            logging.error("failed to stop encoder")
            return {"success": False}

    if command["action"] in ["restart", "start"]:
        if not encoder_mgr.start(command["inputs"], command["output"]):
            logging.error("failed to start encoder")
            return {"success": False}

    return {"success": True}


if __name__ == "__main__":
    logging.config.dictConfig(config.LOGGING)
    http_server = HTTPServer((config.HOST, config.PORT), _CommandHandler)
    http_server.serve_forever()
