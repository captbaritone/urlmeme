import re
import logging
import json
import os

from flask import Flask, send_from_directory, send_file, render_template, request

from memegenerator import gen_meme
from ngram import NGram
from hashlib import md5
from logging.handlers import RotatingFileHandler

APP_ROOT = os.path.dirname(__file__)
MEME_PATH = os.path.join(APP_ROOT, 'static/memes/')
TEMPLATES_PATH = os.path.join(APP_ROOT, 'templates/memes/')
IMAGE_EXTENSIONS = ('png', 'jpeg', 'jpg', 'gif')
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS + ('json', 'log')

app = Flask(__name__)

# Maps meme's file name to its common names
with open(os.path.join(APP_ROOT, 'memes.json')) as data_file:
    MEMES = json.load(data_file)


def replace_underscore(string):
    return re.sub(r'_', ' ', string)


def tokenize(string):
    return re.sub(r' ', '', string.lower())


def parse_meme_url(path):
    """
    Given a URL path, returns a named tuple representing the meme in question
    (meme_name, top_text, bottom_text, extension)
    """
    ext = 'jpg'  # Default extension
    if path.endswith(tuple('.%s' % e for e in SUPPORTED_EXTENSIONS)):
        path, ext = os.path.splitext(path)
        ext = ext[1:]

    path = replace_underscore(path)
    path_parts = path.split('/')[:3]
    while(len(path_parts) < 3):
        path_parts.append('')

    path_parts.append(ext)

    return tuple(path_parts)


def guess_meme_image(meme_name):
    '''
    Guess which meme image they mean by finding the alias with greatest ngram
    similarity
    '''
    meme_name = tokenize(meme_name)
    best = ''
    best_score = None
    for guess_image, names in MEMES.items():
        for guess in names:
            guess = tokenize(guess)
            score = NGram.compare(guess, meme_name)
            if best_score is None or score > best_score:
                best_score = score
                best = guess_image
                app.logger.info('New best meme for "%s": "%s" (Score: %s)', meme_name, guess, score)
    app.logger.info('Picked meme "%s" for name "%s"' % (best, meme_name))
    return best


def meme_file_path(meme_image, top, bottom, ext):
    """ Generate a hash filename for this meme image """

    token = "%s|%s|%s" % (meme_image, top, bottom)
    meme_id = md5(token.encode('utf-8')).hexdigest()
    file_path = '%s.%s' % (meme_id, ext)
    return MEME_PATH + file_path


def meme_image_response(meme_image, top, bottom, ext):
    file_path = meme_file_path(meme_image, top, bottom, ext)
    try:
        open(file_path)
        app.logger.debug('file "%s" exists', file_path)
    except IOError:
        app.logger.info('Generating Meme')
        meme_path = os.path.join(TEMPLATES_PATH, meme_image)
        gen_meme(meme_path + '.jpg', top, bottom, file_path)

    return send_file(file_path)


@app.route("/")
def help():
    return render_template('help.html', base_url=request.base_url)


@app.route('/favicon.ico')
def favicon():
    path = os.path.join(app.root_path, 'static')
    mimetype = 'image/vnd.microsoft.icon'
    return send_from_directory(path, 'favicon.ico', mimetype=mimetype)


@app.route('/<path:path>')
def meme(path):
    meme_name, top, bottom, ext = parse_meme_url(path)
    meme_image = guess_meme_image(meme_name)

    if ext == 'log':
        return meme_image
    elif ext == 'json':
        return json.dumps({'image': meme_image, 'top': top, 'bottom': bottom})
    elif ext in IMAGE_EXTENSIONS:
        return meme_image_response(meme_image, top, bottom, ext)

if __name__ == "__main__":
    handler = RotatingFileHandler(
            os.path.join(APP_ROOT, 'access.log'),
            maxBytes=10000,
            backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()
