from setuptools import setup
from os import path
import telenotify


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='telenotify',
    version=telenotify.version,
    url='https://github.com/s-razoes/telenotify',
    # GitHub releases in format "updog-X.Y"
    download_url = 'https://github.com/s-razoes/telenotify/archive/updog-' + telenotify.version + '.tar.gz',
    license='MIT',
    author='s-razoes',
    author_email='srzgtfo@gmail.com',
    description='Simple telegram interaction module. ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='Telegram Bot Notify',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Requests',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Communications :: File Sharing',
        'Topic :: Communications :: Real time notification',
        'Topic :: Telegram'
    ],
    packages=['telenotify'],
    entry_points={
        'console_scripts': 'telenotify = telenotify.__main__:main'
    },
    include_package_data=True,
    install_requires=[
        'requests',
        'argparse'
    ],
)
