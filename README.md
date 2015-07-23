## Introduction

[slack-alert](https://github.com/dongweiming/slack-alert) is a tool that can send message into slack"s channel when this need be alerted.

**At present only support Python3** it use [AST](https://docs.python.org/3/library/ast.html) compile and parse code and use [apscheduler](http://apscheduler.readthedocs.org/) execute jobs.
the default scheduler use `AsyncIOScheduler`. but we also support:

* TornadoScheduler
* BackgroundScheduler
* GeventScheduler

## Installation

$ pip install slack-alert

you can copy [slack_alert.conf](https://github.com/dongweiming/slack-alert/blob/master/slack_alert.conf) to your config path.

use `OS X` or `linux`. you can copy it to `~/.config/slack_alert.conf`. use `windows` this path is `~\.slack_alert.conf`

you need go http://api.slack.com/web generate token and modify `slack_alert.conf`

## Example plugin

the jobs is put in a directory named `plugins`.

```bash
tree plugins
plugins
├── examples.py

0 directories, 1 files
```

```python
cat plugins/examples.py
# coding=utf-8
import os
@deco(seconds=2)  # this function will be a job. because it has a decorator that contains `hours|seconds|minutes|days`
def a():
    print(1)  # you need use python3's syntax
    print(os)  # you can also use some imported module in local
    return 1  # this return value will be send the specified channel


def b():  # this function will not be a job
    print(3)
    return 2


@deco2(xx=1)
@deco(minutes=2, seconds=30)
def c():  # this function will not be a job. because decorator `deco` need in the outside
    print(4)
    return 3
```

## Usage

Switch to the directory you want to execute jobs. and this directory must has s subdirectory named `plugins`

And you only execute this:

```bash
$slack-alert
```

enjoy it
