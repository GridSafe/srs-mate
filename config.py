import os


# 监听主机名
LISTEN_HOST = os.environ.get("LISTEN_HOST", "")
# 监听端口好
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "8787"))
# ffmpeg可执行文件路径
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "ffmpeg")

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

MAX_NUMBER_OF_ENCODERS = 65536
