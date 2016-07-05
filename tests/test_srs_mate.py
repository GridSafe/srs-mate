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
                    "is_mute": True,
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
                "background_color": 0xFFFFFF,
                "video_bitrate": 480,
                "audio_bitrate": 320
            }
        }

        result = srs_mate._handle_command(start_command)
        self.assertTrue(result["success"])

        restart_command = {
            "action": "restart",
            "output_id": result["output_id"],
            "inputs": [
                {
                    "is_mute": True,
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
                "background_color": 0xFFFFFF,
                "video_bitrate": 480,
                "audio_bitrate": 320
            }
        }

        result = srs_mate._handle_command(restart_command)
        self.assertTrue(result["success"])

        stop_command = {
            "action": "stop",
            "output_id": result["output_id"]
        }

        result = srs_mate._handle_command(stop_command)
        self.assertTrue(result["success"])
