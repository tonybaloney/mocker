import os
import json
from terminaltables import AsciiTable

from mocker import _base_dir_
from .base import BaseDockerCommand


class ImagesCommand(BaseDockerCommand):
    registry_base = 'https://registry-1.docker.io/v2'

    def __init__(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        images = [['name', 'version', 'size']]

        for image_file in os.listdir(_base_dir_):
            if image_file.endswith('.json'):
                with open(os.path.join(_base_dir_, image_file), 'r') as json_f:
                    image = json.loads(json_f.read())
                image_base = os.path.join(_base_dir_, image_file.replace('.json', ''), 'layers')
                size = sum(os.path.getsize(os.path.join(image_base, f)) for f in
                           os.listdir(image_base)
                           if os.path.isfile(os.path.join(image_base, f)))
                images.append([image['name'], image['tag'], sizeof_fmt(size)])

        table = AsciiTable(images)
        print(table.table)


def sizeof_fmt(num, suffix='B'):
    ''' Credit : http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size '''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)