[![Build Status](https://travis-ci.org/captbaritone/urlmeme.svg?branch=master)](https://travis-ci.org/captbaritone/urlmeme)

# urlme.me

A meme generator where the URL is the user interface.

    http://urlme.me/<meme_image>/<top_text>/<bottom_text>.<ext>

# How?

I keep a list of meme images which I think make the cut in `memes.json`. I then
use [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) comparison to find the
closes meme to the image you specified.

# Ussage

Some additional features are offered, also via the URL:

* Request a meme with the extension `.json` to get results in the form: `{"image": "success-kid", "top": "typed a url", "bottom": "made a meme"}`.
* Pass query params `?host=imgur` to have the image uploaded to [Imgur](http://imgur.com/) and then have your request 301 redirected to that Imgur URL.

# Setup

    pip install -r requirements.txt
    python url.py

# Run the tests

    python tests.py

# Contribute

If there is a popular meme image that you think I'm missing, please either file
an issue, or open a pull request. To add an image, simply add the image to:

    templates/memes/

And then add a reference to `memes.json` and include at least one name for that
meme image.
