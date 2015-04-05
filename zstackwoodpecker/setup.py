from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='zstackwoodpecker',
      version=version,
      description="zstack integration test framework",
      long_description="""\
zstack integraion test framework""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='zstack python integration test',
      author='Frank Zhang',
      author_email='xing5820@gmail.com',
      url='http://zstack.org',
      license='Apache License 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'zstacktestagent',
          'ansible',
          'zstacklib',
          'apibinding'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
