from decouple import config

TP_APP_VERSION = config("APP_VERSION", default=None)
