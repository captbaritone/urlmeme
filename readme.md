[![Build Status](https://travis-ci.org/captbaritone/urlmeme.svg?branch=master)](https://travis-ci.org/captbaritone/urlmeme)

# urlme.me

A meme generator where the URL is the user interface.

    http://urlme.me/<meme_image>/<top_text>/<bottom_text>.png

# How?

I keep a list of meme images which I think make the cut in `memes.json`. I then
use [N-gram](https://en.wikipedia.org/wiki/N-gram) comparison to find the
closes meme to the image you specified.

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
