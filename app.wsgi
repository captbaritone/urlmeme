#!/usr/bin/python
import os
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/meme-url/")


def application(environ, start_response):
    for key in ['IMGUR_CLIENT_ID', 'IMGUR_CLIENT_SECRET']:
        os.environ[key] = environ.get(key, '')
    from url import app as _application
    _application.secret_key = 'Add your secret key'
    return _application(environ, start_response)
