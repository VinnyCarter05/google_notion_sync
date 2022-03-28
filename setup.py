# to set up package
# need to start with virtual environment 
# then need to pip install -e . (from root directory of package)
# pip freeze to check

from setuptools import setup, find_packages

setup(name='google_notion_sync', version='1.0', packages=find_packages())