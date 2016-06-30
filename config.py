import logging


HOST = ""
PORT = 8787
FFMPEG_PATH = "ffmpeg"
SRS_HOST = "127.0.0.1"
SRS_PORT = 1935

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
            "class": "logging.FileHandler",
            "formatter": "local",
	    "localname": "srs_mate.log"
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
