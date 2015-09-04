import re
import logging
import json
import os

from flask import Flask, send_from_directory, render_template, request

from memegenerator import gen_meme
from ngram import NGram
import md5
from logging.handlers import RotatingFileHandler

APP_ROOT = os.path.dirname(__file__)
MEME_PATH = os.path.join(APP_ROOT, 'static/memes/')

app = Flask(__name__)

# Maps meme's file name to its common names
with open(os.path.join(APP_ROOT, 'memes.json')) as data_file:
    MEMES = json.load(data_file)


def replace_underscore(string):
    return re.sub(r'_', ' ', string)


def tokenize(string):
    string = re.sub(r' ', '', string)
    return replace_underscore(string.lower())


def guess_meme_image(meme_name):
    '''
    Guess which meme image they mean by finding the alias with greatest ngram
    similarity
    '''
    meme_name = tokenize(meme_name)
    best = '404'
    best_score = None
    for guess_image, names in MEMES.iteritems():
        for guess in names:
            guess = tokenize(guess)
            score = NGram.compare(guess, meme_name)
            if best_score is None or score > best_score:
                best_score = score
                best = guess_image
    app.logger.info('Pick meme %s for name "%s"' % (best, meme_name))
    return best


@app.route("/")
def help():
    return render_template('help.html', base_url=request.base_url)


@app.route('/<path:path>')
def meme(path):
    if path.endswith(('.png', '.jpg')):
        path = path[:-4]

    path_parts = path.split('/')
    while(len(path_parts) < 3):
        path_parts.append('')

    meme_name, top, bottom = tuple(path_parts)

    meme_image = guess_meme_image(meme_name)
    meme_path = os.path.join(APP_ROOT, 'templates/memes/', meme_image)
    top = replace_underscore(top)
    bottom = replace_underscore(bottom)

    meme_id = md5.new("%s|%s|%s" % (meme_image, top, bottom)).hexdigest()
    file_path = '%s.png' % meme_id
    try:
        open(MEME_PATH + file_path)
        app.logger.debug('file exists')
    except IOError:
        app.logger.error('Generating Meme')
        gen_meme(meme_path + '.jpg', top, bottom, MEME_PATH + file_path)

    return send_from_directory(MEME_PATH, file_path)

if __name__ == "__main__":
    handler = RotatingFileHandler(
            os.path.join(APP_ROOT, 'access.log'),
            maxBytes=10000,
            backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()
