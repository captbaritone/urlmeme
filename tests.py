import json
import os
import unittest

from url import APP_ROOT, TEMPLATES_PATH
from url import replace_underscore
from url import tokenize
from url import guess_meme_image
from url import meme


# Maps meme's file name to its common names
with open(os.path.join(APP_ROOT, 'memes.json')) as data_file:
    MEMES = json.load(data_file)


class TestMemeTemplates(unittest.TestCase):

    def test_all_images_exist(self):
        for meme_name in MEMES.keys():
            meme_path = os.path.join(TEMPLATES_PATH, '%s.jpg' % meme_name)
            self.assertTrue(os.path.isfile(meme_path), 'Missing meme template: %s' % meme_path)

    def test_no_extra_images_exist(self):
        for meme_template in os.listdir(TEMPLATES_PATH):
            if meme_template in ['.DS_Store']:
                continue
            self.assertTrue(meme_template.endswith('.jpg'), "Found non jpg file: %s" % meme_template)
            meme_name = meme_template[:-4]
            self.assertIn(meme_name, MEMES.keys(), "Found extra jpg file: %s" % meme_template)


class TestStringFunctions(unittest.TestCase):

    def test_replace_underscore(self):
        self.assertEqual('hello world', replace_underscore('hello world'))

    def test_tokenize(self):
        self.assertEqual('helloworld', tokenize('hello world'))


class TestMemeGuesser(unittest.TestCase):

    def test_guess_meme_image(self):
        self.assertEqual('success-kid', guess_meme_image('success'))


class TestMemeJson(unittest.TestCase):

    def test_meme_json(self):
        meme_json = json.loads(meme('success/made_an_assertion/tests_passed.json'))
        expected = {
            u'image': u'success-kid',
            u'top': u'made an assertion',
            u'bottom': u'tests passed'
        }
        self.assertEqual(expected, meme_json)


if __name__ == '__main__':
    unittest.main()
