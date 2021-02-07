# -*- coding:UTF-8 -*-
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import image

image_ops = None

def test():
    global image_ops
    image_ops = image.IMAGE()
    image_ops.add_image()
    # image_ops.add_image(adding_type='file', local_file='C:\\Users\\Administrator\\Desktop\\centos7-test.qcow2')
    image_ops.check_browser_console_log()
    test_util.test_pass('Add Image Successful')

def env_recover():
    global image_ops
    image_ops.expunge_image()
    image_ops.close()

def error_cleanup():
    global image_ops
    try:
        image_ops.expunge_image()
        image_ops.close()
    except:
        pass
