import unittest
import unittest.mock

import srs_mate


class TestSrsMate(unittest.TestCase):
    @unittest.mock.patch("config.FFMPEG_PATH", "test")
    def test_handle_command(self):
        start_command = {
            "action": "start",
            "inputs": [
                {
                    "source": "rtmp://localhost/test/test1",
                    "left": 0,
                    "top": 0,
                    "width": 480,
                    "height": 270
                },
                {
                    "source": "rtmp://localhost/test/test2",
                    "left": 800,
                    "top": 450,
                    "width": 480,
                    "height": 270
                }
            ],
            "output": {
                "target": {
                    "vhost": "localhost",
                    "app": "test",
                    "stream": "test3"
                },
                "width": 1280,
                "height": 720,
                "background": 0xFFFFFF
            }
        }

        self.assertEqual(srs_mate._handle_command(start_command), {"success": True})

        restart_command = {
            "action": "restart",
            "inputs": [
                {
                    "source": "rtmp://localhost/test/test2",
                    "left": 0,
                    "top": 0,
                    "width": 480,
                    "height": 270
                },
                {
                    "source": "rtmp://localhost/test/test1",
                    "left": 800,
                    "top": 450,
                    "width": 480,
                    "height": 270
                }
            ],
            "output": {
                "target": {
                    "vhost": "localhost",
                    "app": "test",
                    "stream": "test3"
                },
                "width": 1280,
                "height": 720,
                "background": 0xFFFFFF
            }
        }

        self.assertEqual(srs_mate._handle_command(restart_command), {"success": True})

        stop_command = {
            "action": "stop",
            "output": {
                "target": {
                    "vhost": "localhost",
                    "app": "test",
                    "stream": "test3"
                },
                "width": 0,
                "height": 0
            }
        }

        self.assertEqual(srs_mate._handle_command(stop_command), {"success": True})
