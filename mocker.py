#!/usr/bin/python
from docopt import docopt

import mocker
from mocker.base import BaseDockerCommand
from mocker.pull import PullCommand

if __name__ == '__main__':
    arguments = docopt(mocker.__doc__, version=mocker.__version__)
    command = BaseDockerCommand
    if arguments['pull']:
        command = PullCommand

    cls = command(**arguments)
    cls.run(**arguments)
