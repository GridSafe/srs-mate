from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

import config
import encoder_mgr


class MainHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/command":
            self.send_response(404)
            self.end_headers()
            return

        try:
            command = json.loads(self.rfile.read(int(self.headers["Content-Length"]))
                                 .decode("utf-8"))
            result = json.dumps(handle_command(command)).encode("utf-8")
        except:
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(result)


def validate_command(command):
    if "action" not in command:
        return False

    if command["action"] != "start" and command["action"] != "stop":
        return False

    if command["action"] == "start":
        if "inputs" not in command:
            return False

        if not isinstance(command["inputs"], list):
            return False

    if "output" not in command:
        return False

    if not isinstance(command["output"], dict):
        return False

    return True


def handle_command(command):
    if not validate_command(command):
        logging.error("invalid command={}".format(command))
        return {"success": False}

    if command["action"] == "start":
        if not encoder_mgr.start(command["inputs"], command["output"]):
            logging.error("failed to start encoder")
            return {"success": False}
    else:
        if not encoder_mgr.stop(command["output"]):
            logging.error("failed to stop encoder")
            return {"success": False}

    return {"success": True}


logging.basicConfig(filename=config.LOGGING_FILE_NAME, level=config.LOGGING_LEVEL
                    , format=config.LOGGING_FORMAT)

http_server = HTTPServer(("", config.PORT), MainHandler)
http_server.serve_forever()
