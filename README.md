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

you can visit https://api.slack.com/methods/chat.postMessage get all keys for `slack_alert.conf`

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

### Config file"s Options

```bash
cat ~/.config/slack_alert.conf

[slack]
token = xoxp-4231087425-4231087427-4463321974-03174a  # you need go http://api.slack.com/web register token
channel = test  # which channel will receive your jobs results. also you can send the message to someone directly. this is user's id.
username = MovieBot  # name of bot.
icon_url = ''  # URL to an image to use as the icon for this message
icon_emoji = :fire:  # emoji to use as the icon for this message. Overrides icon_url.
working_hours = ''  # only time in working_hours jobs is work. format: `9:30-19:00`,`9:00-12:00,13:00-18:00`
```

### Command Options

```bash
slack-alert --version  # get current version and quit
slack-alert --config ~/new/path/slack-alert.conf  # used a new config path
slack-alert --ignore-global-config  # the local config is ignored
slack-alert --scheduler GeventScheduler # You can choice scheduler type in (AsyncIOScheduler, BackgroundScheduler, GeventScheduler, TornadoScheduler). default is AsyncIOScheduler
slack-alert --path  # default the jobs files is in current path"s `plugins` sub directory. you can use other path"s `plugins` sub directory.
slack-alert --working-hours # it's same as above
slack-alert --max-alert  # If you don't want receive all message in channel. you can use this. this job will send count don't exceed this limit until the pause time pass
slack-alert --pause-time  # If receive get to the limit. we stop some minutes.


```


enjoy it
