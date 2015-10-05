import json
import os
from mock import patch
from unittest import TestCase, skip, skipIf, main

from url import APP_ROOT, TEMPLATES_PATH, ERROR_BACKGROUND
from url import replace_underscore
from url import tokenize
from url import guess_meme_image
from url import parse_meme_url
from url import derive_meme_path
from url import app

ON_TRAVIS = "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true"


# Maps meme's file name to its common names
with open(os.path.join(APP_ROOT, 'memes.json')) as data_file:
    MEMES = json.load(data_file)


class FlaskTestCase(TestCase):

    def setUp(self):
        self.app = app.test_client()


class TestMemeTemplates(TestCase):

    def test_error_background_exists(self):
        self.assertIn(ERROR_BACKGROUND, MEMES.keys())

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


class TestStringFunctions(TestCase):

    def test_replace_underscore(self):
        self.assertEqual('hello world', replace_underscore('hello world'))

    def test_tokenize(self):
        self.assertEqual('helloworld', tokenize('hello world'))
        self.assertEqual('helloworld', tokenize('HELLOWORLD'))


class TestMemeUrlParser(TestCase):

    def test_underscores_are_replaced_with_spaces(self):
        expected = '  foo', 'bar  ', 'b  az', 'jpg'
        self.assertEqual(expected, parse_meme_url('__foo/bar__/b__az.jpg'))

    def test_discards_extra_arguments(self):
        expected = 'foo', 'bar', 'baz', 'jpg'
        self.assertEqual(expected, parse_meme_url('foo/bar/baz/boop.jpg'))

    def test_handles_too_few_arguments(self):
        expected = 'foo', '', '', 'jpg'
        self.assertEqual(expected, parse_meme_url('foo.jpg'))

    def test_dots_are_preserved(self):
        expected = '...', '...', 'bar', 'jpg'
        self.assertEqual(expected, parse_meme_url('.../.../bar.jpg'))

    def test_unknown_file_extension(self):
        expected = 'foo', 'bar', 'baz.bloop', 'jpg'
        self.assertEqual(expected, parse_meme_url('foo/bar/baz.bloop'))

    @skip('path.splittext() is to blame')
    def test_dots_in_bottom_text_are_preserved(self):
        expected = 'foo', 'bar', '...', 'jpg'
        self.assertEqual(expected, parse_meme_url('foo/bar/....jpg'))


class TestMemeGuesser(TestCase):

    def test_guess_meme_image(self):
        self.assertEqual('success-kid', guess_meme_image('success'))

    def test_handles_simple_typos(self):
        self.assertEqual('success-kid', guess_meme_image('success kyd'))

    def test_handles_blank_image(self):
        for name in ['', ' ', 'blank']:
            self.assertEqual('blank-colored-background', guess_meme_image(name))


class TestMemeFilePath(TestCase):

    def test_hash(self):
        path = derive_meme_path('foo', 'bar', 'baz', 'jpg')
        self.assertTrue(path.endswith('04a4ab04fa79a4d325adc397d9b3e6bd.jpg'))

        path = derive_meme_path('foo', 'bar', 'baz', 'png')
        self.assertTrue(path.endswith('04a4ab04fa79a4d325adc397d9b3e6bd.png'))

    def test_emojis(self):
        path = derive_meme_path('success-kid', u'\xf0', u'\xf0', 'jpg')
        self.assertTrue(path.endswith('42025951d83a7977a4e5843c7c1d7e15.jpg'))


class TestMemeResponse(FlaskTestCase):

    def test_meme_json(self):
        response = self.app.get('success/made_an_assertion/tests_passed.json')
        expected = {
            u'image': u'success-kid',
            u'top': u'made an assertion',
            u'bottom': u'tests passed'
        }
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, json.loads(response.get_data(as_text=True)))

    @skipIf(ON_TRAVIS, 'Image generation does not work on Travis yet')
    @patch('imgur.upload', return_value='http://imgur.com/MOCK_RESULT')
    def test_imgur_redirect(self, mock_upload):
        response = self.app.get('success/uploaded/to_imgur.jpg?host=imgur')
        self.assertEqual(301, response.status_code)
        self.assertEqual('http://imgur.com/MOCK_RESULT', response.location)

    @skipIf(ON_TRAVIS, 'Image generation does not work on Travis yet')
    def test_good_image_response(self):
        response = self.app.get('success/made_an_assertion/tests_passed.jpg')
        self.assertEqual(200, response.status_code)
        self.assertEqual('image/jpeg', response.mimetype)

    @skipIf(ON_TRAVIS, 'Image generation does not work on Travis yet')
    def test_png_response(self):
        response = self.app.get('success/made_an_assertion/tests_passed.png')
        self.assertEqual(200, response.status_code)
        self.assertEqual('image/png', response.mimetype)

    @skipIf(ON_TRAVIS, 'Image generation does not work on Travis yet')
    def test_gif_response(self):
        response = self.app.get('success/made_an_assertion/tests_passed.gif')
        self.assertEqual(200, response.status_code)
        self.assertEqual('image/gif', response.mimetype)


if __name__ == '__main__':
    main()
