import os
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

CLIENT_ID = str(os.environ.get("IMGUR_CLIENT_ID"))
CLIENT_SECRET = str(os.environ.get("IMGUR_CLIENT_SECRET"))


class ImgurException(Exception):
    def __init__(self, message):
        self.message = message


def upload(image_path):
    """ Takes a file path, and returns it's URL on Imgur """
    try:
        client = ImgurClient(CLIENT_ID, CLIENT_SECRET)
        imgur_response = client.upload_from_path(image_path)
    except ImgurClientError as e:
        raise ImgurException(e.error_message)
    return imgur_response['link']
