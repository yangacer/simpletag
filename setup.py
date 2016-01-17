try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import simpletag

__clsfrs__ = [
    "Programming Language :: Python :: 2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

setup(name="simpletag",
      version=simpletag.__version__,
      author="Acer.Yang",
      author_email="yangacer@gmail.com",
      url="https://pypi.python.org/pypi/simpletag",
      py_modules=["simpletag"],
      description="Plug-n-Play Simple Tag Library",
      license="MIT",
      classifiers=__clsfrs__
      )
