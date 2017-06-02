from os.path import dirname, join
from setuptools import setup


version = '0.2.0'


def read(fname):
    return open(join(dirname(__file__), fname)).read()


with open("requirements.txt", "r'") as f:
    install_reqs = f.readlines()

setup(name='speed_performance_tracker',
      version=version,
      author="Chad Dotson",
      author_email="chad@cdotson.com",
      description="Tools for recording, graphing, reporting connection and website performance",
      license="GNUv3",
      keywords=["bandwidth", "test",],
      url="https://github.com/chaddotson/website_latency_tracker",
      download_url = 'https://github.com/chaddotson/website_latency_tracker/tarball/0.2.0',
      packages=['scripts'],
      long_description=read("README.rst"),
      install_requires=install_reqs,
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'graph_connection_speed = scripts.graph_connection_speed:main',
              'graph_site_responses = scripts.graph_site_responses:main',
              'record_connection_speed = scripts.record_connection_speed:main',
              'record_site_responses = scripts.record_site_responses:main'
          ]
      },
      classifiers=[
          "Development Status :: 4 - Beta",
          "Topic :: Utilities",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      ],
      test_suite='nose.collector',
      tests_require=['nose'],

)
