from setuptools import setup, find_packages
import sys, os

version = '1.0.0'

setup(name='zstacktestagent',
      version=version,
      description="zstack integration test agent",
      long_description="""\
zstack integration test agent""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='zstack integration test python',
      author='Frank Zhang',
      author_email='xing5820',
      url='http://zstack.org',
      license='Apache License 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
