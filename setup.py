import os
from distutils.core import setup
from django.core.management.commands.compilemessages import compile_messages
from friends import __version__, __maintainer__, __email__


def compile_translations():
    curdir = os.getcwdu()
    os.chdir(os.path.join(os.path.dirname(__file__), 'friends'))
    compile_messages()
    os.chdir(curdir)
compile_translations()


license_text = open('LICENSE.txt').read()
long_description = open('README.rst').read()


setup(
    name = 'django-simple-friends',
    version = __version__,
    url = 'http://github.com/muhuk/django-simple-friends',
    author = __maintainer__,
    author_email = __email__,
    license = license_text,
    packages = ['friends', 'friends.templatetags'],
    package_data= {'friends': ['fixtures/*.json',
                               'locale/*/LC_MESSAGES/django.*']},
    data_files=[('', ['LICENSE.txt', 'README.rst'])],
    description = 'Like django-friends, but simpler',
    long_description=long_description,
    classifiers = ['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
)
