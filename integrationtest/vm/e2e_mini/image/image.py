# -*- coding:utf-8 -*-

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib

test_stub = test_lib.lib_get_test_stub()
from test_stub import *


class IMAGE(MINI):
    def __init__(self, uri=None, initialized=False):
        self.image_name = None
        self.image_list = []
        if initialized:
            # if initialized is True, uri should not be None
            self.uri = uri
            return
        super(IMAGE, self).__init__()

    def add_image(self, name=None, dsc=None, adding_type='url', url=None, local_file=None, platform='Linux', view='card'):
        self.image_name = name if name else 'image-' + get_time_postfix()
        self.image_list.append(self.image_name)
        url = url if url else os.getenv("imageUrl_net")
        test_util.test_logger('Add Image [%s]' % self.image_name)
        priority_dict = {'type': adding_type}
        image_dict = {'name': self.image_name,
                      'description': dsc,
                      'url': url,
                      'file': local_file,
                      'platform': platform}
        if adding_type == 'url':
            image_dict.pop('file')
        elif adding_type == 'file':
            image_dict.pop('url')
        image_elem = self.create(image_dict, "image", view=view, priority_dict=priority_dict)
        check_list = [self.image_name, url.split('.')[-1]]
        checker = MINICHECKER(self, image_elem)
        checker.image_check(check_list)

    def delete_image(self, image_name=None, view='card', corner_btn=True, details_page=False):
        image_name = image_name if image_name else self.image_list
        self.delete(image_name, 'image', view=view, corner_btn=corner_btn, details_page=details_page)

    def expunge_image(self, image_name=None, view='card', details_page=False):
        image_name = image_name if image_name else self.image_list
        self.delete(image_name, 'image', view=view, expunge=True, details_page=details_page)
