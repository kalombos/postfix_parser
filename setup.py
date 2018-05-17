# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


if __name__ == '__main__':
    setup(name='postfix_parser',
          version='0.0.1',
          url="https://github.com/kalombos/postfix_parser",
          download_url="https://github.com/kalombos/postfix_parser",
          description='Postfix parser',
          long_description="The tool can report stats about sent emails from postfix log.",
          author='Nikolay Gorshkov',
          author_email='nogamemorebrain@gmail.com',
          maintainer='kalombo',
          maintainer_email='nogamemorebrain@gmail.com',
          packages=find_packages(),
          keywords=['postfix', 'python', 'parser'],
)
