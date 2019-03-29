import re
import json
import os
import logging
import time

from logging.handlers import RotatingFileHandler
from logging import Formatter
from fuzzywuzzy import fuzz
from hashlib import md5

from flask import Flask, jsonify, send_from_directory, send_file, render_template, request, redirect

import imgur
from memegenerator import gen_meme

APP_ROOT = os.path.dirname(__file__)
MEME_PATH = os.path.join(APP_ROOT, 'static/memes/')
TEMPLATES_PATH = os.path.join(APP_ROOT, 'templates/memes/')
IMAGE_EXTENSIONS = ('png', 'jpeg', 'jpg', 'gif')
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS + ('json',)
ERROR_BACKGROUND = 'blank-colored-background'

UPLOAD_FOLDER = os.path.join(APP_ROOT, 'user_uploads/')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Limit uploads to 2mb. This limit is also enforced in the client
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Logging
handler = RotatingFileHandler(os.path.join(
    APP_ROOT, 'urlmeme.log'), maxBytes=10000, backupCount=1)
handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s'))
handler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Maps meme's file name to its common names
with open(os.path.join(APP_ROOT, 'memes.json')) as data_file:
    MEMES = json.load(data_file)

def get_hash_from_custom_image(meme_name):
    m = re.match(r"^uploaded-([a-f0-9]{32})$", meme_name)
    return m and m.groups()[0]

def is_custom_image(meme_name):
    return get_hash_from_custom_image(meme_name) is not None

def get_template_path(meme_name):
    if(is_custom_image(meme_name)):
        hash = get_hash_from_custom_image(meme_name)
        return os.path.join(UPLOAD_FOLDER, hash)

    return os.path.join(TEMPLATES_PATH, meme_name)

def get_ext(filename):
    return "." in filename and filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return get_ext(filename) in ALLOWED_EXTENSIONS

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
            if(meme_name == guess):
                score = 100
            else:
                # Add spaces to prefer matches that have word boundaries
                score = fuzz.partial_ratio(guess, " " + meme_name + " ")
            if best_score is None or score > best_score:
                best_score = score
                best = guess_image
                app.logger.debug(
                    'New best meme for "%s": "%s" (Score: %s)', meme_name, guess, score)
    app.logger.info('Picked meme "%s" for name "%s" (Score: %s)',
                    best, meme_name, best_score)
    return best


def derive_meme_path(meme_image, top, bottom, ext):
    """ Generate a hash filename for this meme image """

    token = "%s|%s|%s" % (meme_image, top, bottom)
    meme_id = md5(token.encode('utf-8')).hexdigest()
    file_path = '%s.%s' % (meme_id, ext)
    return MEME_PATH + file_path


def meme_image_path(meme_image, top, bottom, ext):
    file_path = derive_meme_path(meme_image, top, bottom, ext)
    app.logger.debug('Looking for file: "%s"', file_path)
    if os.path.exists(file_path):
        app.logger.info('Found meme in cache: "%s"', file_path)
    else:
        app.logger.info('Generating "%s"', file_path)
        meme_path = get_template_path(meme_image)
        gen_meme(meme_path + '.jpg', top, bottom, file_path)

    return file_path


def error_image_response(top, bottom, status=500):
    app.logger.error('Sending error response: %s, %s (%s)',
                     top, bottom, status)
    image_path = meme_image_path(ERROR_BACKGROUND, top, bottom, 'jpg')
    return send_file(image_path), status


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
    app.logger.info('New request for meme: "%s"', path)
    meme_name, top, bottom, ext = parse_meme_url(path)
    if is_custom_image(meme_name):
        meme_image = meme_name
    else:
        meme_image = guess_meme_image(meme_name)

    app.logger.info('Meme: "%s" / "%s" / "%s" . "%s"',
                    meme_image, top, bottom, ext)
    if ext == 'json':
        app.logger.info('Serving JSON')
        return json.dumps({'image': meme_image, 'top': top, 'bottom': bottom, 'custom': is_custom_image(meme_name)})
    elif ext in IMAGE_EXTENSIONS:
        image_path = meme_image_path(meme_image, top, bottom, ext)

        host = request.args.get('host', None)
        if host == 'imgur':
            try:
                imgur_url = imgur.upload(image_path)
                app.logger.info('Uploaded: "%s" as "%s"',
                                image_path, imgur_url)
                app.logger.info('Redirecting to: "%s"', imgur_url)
                return redirect(imgur_url, code=301)
            except imgur.ImgurException as e:
                return error_image_response('Error uploading "%s" to Imgur:', image_path, e.message)

        app.logger.info('Serving: "%s"', image_path)
        return send_file(image_path)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('No selected file')
        return make_response(jsonify({"reason": "No selected file"}), 400)
    file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected filename')
        return make_response(jsonify({"reason": "Missing a filename"}), 400)
    if file and allowed_file(file.filename):
        ext = get_ext(file.filename)
        hash = md5(file.stream.read()).hexdigest()
        file.seek(0)
        meme_name = "uploaded-%s" % hash
        filepath = "%s.%s" % (get_template_path(meme_name), "jpg")
        file.save(filepath)
        image_info = {
            "meme_name": meme_name,
            "filename": file.filename,
            "md5": hash,
            "upload_time": time.time(),
            "ip": request.remote_addr
        }
        metadata_path = os.path.join(UPLOAD_FOLDER, "%s.json" % hash)
        with open(metadata_path, 'w') as f:  
            json.dump(image_info, f, indent=2)
        return jsonify(image_info)

if __name__ == "__main__":
    """ Only runs in dev """
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True)
