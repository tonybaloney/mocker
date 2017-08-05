import os
import colorama
import logging
import sys

__copyright__ = """
   Copyright 2016 Anthony Shaw

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
__version__ = '1.0.0'

__doc__ = """Mocker.

Usage:
  mocker pull <name>[<tag>]
  mocker run <name>
  mocker images
  mocker (-h | --help)
  mocker --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

_base_dir_ = os.path.join(os.path.expanduser('~'), 'mocker')

if not os.path.exists(_base_dir_):
    os.makedirs(_base_dir_)


# Courtesy http://plumberjack.blogspot.com/2010/12/colorizing-logging-output-in-terminals.html
# Tweaked to use colorama for the coloring


class ColorizingStreamHandler(logging.StreamHandler):
    color_map = {
        logging.DEBUG: colorama.Style.DIM + colorama.Fore.CYAN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Back.RED,
    }

    def __init__(self, stream, color_map=None):
        logging.StreamHandler.__init__(self,
                                       colorama.AnsiToWin32(stream).stream)
        if color_map is not None:
            self.color_map = color_map

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize a traceback
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message

    def colorize(self, message, record):
        try:
            return (self.color_map[record.levelno] + message +
                    colorama.Style.RESET_ALL)
        except KeyError:
            return message

log = logging.getLogger()
handler = ColorizingStreamHandler(sys.stdout)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.INFO)
