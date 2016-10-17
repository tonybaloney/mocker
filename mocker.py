#!/usr/bin/python
from docopt import docopt

import mocker
from mocker.base import BaseDockerCommand
from mocker.pull import PullCommand
from mocker.images import ImagesCommand

if __name__ == '__main__':
    arguments = docopt(mocker.__doc__, version=mocker.__version__)
    command = BaseDockerCommand
    if arguments['pull']:
        command = PullCommand
    elif arguments['images']:
        command = ImagesCommand

    cls = command(**arguments)
    cls.run(**arguments)
