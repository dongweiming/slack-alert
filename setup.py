# coding=utf-8
import sys

from setuptools import setup


def get_version():
    with open('slack_alert.py') as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


install_requires = ['slacker', 'apscheduler', 'tornado', 'gevent==1.1b1']

if sys.version_info.major == 3:
    install_requires.append('asyncio')

setup(
    name='slack-alert',
    version=get_version(),
    py_modules=['slack_alert'],
    description=('Send message onto a channel when '
                 'this need be alerted under Python3'),
    author='DongWeiming',
    author_email='ciici123@gmail.com',
    url='https://github.com/dongweiming/slack-alert',
    install_requires = install_requires,
    license='MIT',
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
    keywords='slack',
    entry_points={'console_scripts': ['slack-alert = slack_alert:main']},
)
