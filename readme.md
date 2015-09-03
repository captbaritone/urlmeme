# urlme.me

A meme generator where the URL is the user interface.

    http://urlme.me/<meme_image>/<top_text>/<bottom_text>.png

# How?

I keep a list of meme images which I think make the cut in `memes.json`. I then
use [N-gram](https://en.wikipedia.org/wiki/N-gram) comparison to find the
closes meme to the image you specified.
