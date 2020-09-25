import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') \
                 or 'qSvvDb5C3wCtD3fqZlylHD0dIVTapLnqIVMOjBiz7s0nYssfO0RXqnto9savrc6vC8Dfhd1WlfEbQxFqXynpFbB9yVK7QtfB'
    SIMPLELOGIN_USERNAME = os.environ.get('SIMPLELOGIN_USERNAME') or 'riego'
    SIMPLELOGIN_PASSWORD = os.environ.get('SIMPLELOGIN_PASSWORD') or '2feb95'
