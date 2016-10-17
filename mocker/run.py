import os

from mocker import _base_dir_
from .base import BaseDockerCommand
from .images import ImagesCommand

try:
    from pychroot import Chroot
except ImportError:
    print('warning: missing chroot options')


class RunCommand(BaseDockerCommand):
    def __init__(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        images = ImagesCommand().list_images()
        image_name = kwargs['<name>']

        match = [i[3] for i in images if i[0] == image_name][0]
        target_file = os.path.join(_base_dir_, match)
        layer_dir = os.path.join(_base_dir_, match.replace('.json', ''), 'layers', 'contents')

        print(layer_dir)
