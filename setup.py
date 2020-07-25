from setuptools import setup, find_packages
import re

VERSIONFILE = "Solos/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='solos',
      version=verstr,
      description='Python implementation of  Solos: A Dataset for Audio-Visual Music Source Separation and Localization',
      url='https://juanfmontesinos.github.io/Solos/',
      author='Juan Montesinos',
      author_email='juanfelipe.montesinos@upf.edu',
      packages=find_packages(),
      install_requires=['Fire', 'youtube_dl', 'googledrivedownloader'],
      package_data={'Solos': 'json_files/solos_ids.json'},
      include_package_data=True,
      classifiers=[
          "Programming Language :: Python :: 3", ],
      zip_safe=False)
