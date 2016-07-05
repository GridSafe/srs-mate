import os


LISTEN_HOST = os.environ.get("LISTEN_HOST", "")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8787"))
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "ffmpeg")
SRS_HOST = os.environ.get("SRS_HOST", "127.0.0.1")
SRS_PORT = int(os.environ.get("SRS_PORT", "1935"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,

    "formatters": {
        "local": {
            "format": "[%(asctime)s][%(levelname)s] %(message)s",
	},
    },

    "handlers": {
        "local": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "local",
	},

        "sentry": {
            "level": "ERROR",
            "class": "raven.handlers.logging.SentryHandler",
            "dsn": "https://<key>:<secret>@app.getsentry.com/<project>",
   	},
    },

    "loggers": {
        "": {
            "handlers": ["local", "sentry"],
            "level": "DEBUG",
            "propagate": False,
	}
    }
}

MAX_NUMBER_OF_OUTPUT = 65536
