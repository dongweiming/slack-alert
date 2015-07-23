# coding=utf-8
''''''
import os
import ast
import sys
import time
import signal
import argparse
import asyncio
from functools import reduce, partial

from slacker import Slacker
from tornado.ioloop import IOLoop
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

try:
    from configparser import ConfigParser as SafeConfigParser, Error
except ImportError:
    from ConfigParser import SafeConfigParser, Error

__version__ = '0.1.3'
desc = 'Send message onto a channel when this need be alerted under Python3'


if sys.platform == 'win32':
    USER_CONFIG = os.path.expanduser(r'~\.slack_alert.conf')
else:
    USER_CONFIG = os.path.join(
        os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config'),
        'slack_alert.conf'
    )


def read_config(args, parser):
    config = SafeConfigParser()
    try:
        config.read(args.config)
        defaults = dict((k.lstrip('-').replace('-', '_'), v)
                        for k, v in config.items('slack'))
        parser.set_defaults(**defaults)
    except Error:
        # Ignore for now.
        pass

    return parser


def create_parser():
    """Return command-line parser."""
    parser = argparse.ArgumentParser(description=desc, prog='slack-alert')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('-c', '--config', metavar='filename',
                        default=USER_CONFIG,
                        help='path to a global config file; if this file '
                             'does not exist then this is ignored '
                             '(default: {0})'.format(USER_CONFIG))
    parser.add_argument('--ignore-global-config', action='store_true',
                        help="don't look for and apply global config files")
    parser.add_argument('-s', '--scheduler', choices=['AsyncIOScheduler',
                                                      'BackgroundScheduler',
                                                      'GeventScheduler',
                                                      'TornadoScheduler'],
                        default='AsyncIOScheduler',
                        help=('You can choosing a scheduler that depends '
                              'mostly on your programming environment'
                              '(default: AsyncIOScheduler)'))
    parser.add_argument('--path', default='.',
                        help=('path to plugins files directory. (default: '
                              'current directory)'))
    return parser


def parse_args(arguments):
    parser = create_parser()
    args = parser.parse_args(arguments)
    if not args.ignore_global_config:
        parser = read_config(args, parser)
        args = parser.parse_args(arguments)
    return args


class GetJobs(ast.NodeTransformer):

    def __init__(self):
        self.jobs = []

    def get_jobs(self):
        return self.jobs

    def get_job_args(self, decorator):
        return {k.arg: k.value.n for k in decorator.keywords
                if k.arg in ('hours', 'seconds', 'minutes', 'days')
                and isinstance(k.value, ast.Num)}

    def visit_FunctionDef(self, node):
        decorator_list = node.decorator_list
        if not decorator_list:
            return node
        decorator = decorator_list[0]
        args = self.get_job_args(decorator)
        if args:
            node.decorator_list = decorator_list[1:]
            self.jobs.append((node.name, args))
        return node


def find_jobs(path):
    jobs = []
    for root, dirs, files in os.walk(path):
        for name in files:
            file = os.path.join(root, name)
            if not file.endswith('.py'):
                continue
            with open(file) as f:
                expr_ast = ast.parse(f.read())
                transformer = GetJobs()
                sandbox = {}
                exec(compile(transformer.visit(expr_ast),
                             '<string>', 'exec'), sandbox)
                jobs.extend([(sandbox[j], kw) for j, kw in transformer.jobs])
    return jobs


def slack_listener(config, event):
    slack = Slacker(config.token)
    if event.retval:
        slack.chat.post_message(
            '#{}'.format(config.channel), event.retval,
            username=config.username, icon_url=config.icon_url,
            icon_emoji=config.icon_emoji)


def _main(args):
    plugins_path = os.path.join(args.path, 'plugins')
    scheduler_name = args.scheduler
    scheduler_module = scheduler_name.lower().replace('scheduler', '')
    if not os.path.isdir(plugins_path):
        print('{} must be exists and is a directory'.format(
            plugins_path))
        return 1

    jobs = find_jobs(plugins_path)
    if not jobs:
        print('Not yet jobs!')
        return 1
    apscheduler = __import__('apscheduler.schedulers.{}'.format(
        scheduler_module))
    scheduler_cls = reduce(lambda x, y: getattr(x, y),
                           [apscheduler.schedulers, scheduler_module,
                            scheduler_name])
    scheduler = scheduler_cls()

    listener = partial(slack_listener, args)
    scheduler.add_listener(listener,
                           EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    for job, kw in jobs:
        scheduler.add_job(job, 'interval', **kw)
    g = scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        if scheduler_name == 'AsyncIOScheduler':
            asyncio.get_event_loop().run_forever()
        elif scheduler_name == 'GeventScheduler':
            g.join()
        elif scheduler_name == 'TornadoScheduler':
            IOLoop.instance().start()
        else:
            while True:
                time.sleep(2)
        return 0
    except (KeyboardInterrupt, SystemExit):
        if scheduler_name not in ('AsyncIOScheduler-', 'GeventScheduler',
                                  'TornadoScheduler'):
            scheduler.shutdown()


def main():
    try:
        # Exit on broken pipe.
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except AttributeError:  # pragma: no cover
        # SIGPIPE is not available on Windows.
        pass

    try:
        args = parse_args(sys.argv[1:])
        return _main(args)
    except KeyboardInterrupt:
        return 1  # pragma: no cover


if __name__ == '__main__':
    main()
