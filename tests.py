from url import APP_ROOT, TEMPLATES_PATH
import json
import os
import unittest


# Maps meme's file name to its common names
with open(os.path.join(APP_ROOT, 'memes.json')) as data_file:
    MEMES = json.load(data_file)


class TestMemeTemplates(unittest.TestCase):

    def test_all_images_exist(self):
        for meme in MEMES.keys():
            meme_path = os.path.join(TEMPLATES_PATH, '%s.jpg' % meme)
            self.assertTrue(os.path.isfile(meme_path), 'Missing meme template: %s' % meme_path)

    def test_no_extra_images_exist(self):
        for meme_template in os.listdir(TEMPLATES_PATH):
            if meme_template in ['.DS_Store']:
                continue
            self.assertTrue(meme_template.endswith('.jpg'), "Found non jpg file: %s" % meme_template)
            meme_name = meme_template[:-4]
            self.assertIn(meme_name, MEMES.keys(), "Found extra jpg file: %s" % meme_template)


if __name__ == '__main__':
    unittest.main()
