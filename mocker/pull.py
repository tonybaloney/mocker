import requests
import os, platform
import json
import tarfile
from mocker import _base_dir_
from .base import BaseDockerCommand


class PullCommand(BaseDockerCommand):
    registry_base = 'https://registry-1.docker.io/v2'

    def __init__(self, *args, **kwargs):
        self.image = kwargs['<name>']
        self.library = 'library'  # todo - user-defined libraries
        self.tag = kwargs['<tag>'] if kwargs['<tag>'] is not None else 'latest'

    def auth(self, library, image):
        # request a v2 token
        token_req = requests.get(
            'https://auth.docker.io/token?service=registry.docker.io&scope=repository:%s/%s:pull'
            % (library, image))
        return token_req.json()['token']

    def get_manifest(self, headers):
        # get the image manifest
        print("Fetching manifest for %s:%s..." % (self.image, self.tag))

        manifest = requests.get('%s/%s/%s/manifests/%s' %
                                (self.registry_base, self.library, self.image, self.tag),
                                headers=self.headers)

        manifest = manifest.json()

    def run(self, *args, **kwargs):
        # login anonymously
        self.headers = {'Authorization': 'Bearer %s' % self.auth(self.library,
                                                                 self.image)}

        # get the manifest
        manifest = self.get_manifest()

        # save the manifest
        image_name_friendly = manifest['name'].replace('/', '_')
        with open(os.path.join(_base_dir_,
                               image_name_friendly+'.json'), 'w') as cache:
            cache.write(json.dumps(manifest))
        # save the layers to a new folder
        dl_path = os.path.join(_base_dir_, image_name_friendly, 'layers')
        if not os.path.exists(dl_path):
            os.makedirs(dl_path)

        # fetch each unique layer
        layer_sigs = [layer['blobSum'] for layer in manifest['fsLayers']]
        unique_layer_sigs = set(layer_sigs)

        # setup a directory with the image contents
        contents_path = os.path.join(dl_path, 'contents')
        if not os.path.exists(contents_path):
            os.makedirs(contents_path)

        for sig in unique_layer_sigs:
            print('Fetching layer %s..' % sig)
            url = '%s/%s/%s/blobs/%s' % (self.registry_base, self.library,
                                         self.image, sig)
            local_filename = os.path.join(dl_path, sig) + '.tar'

            r = requests.get(url, stream=True, headers=self.headers)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            # list some of the contents..
            with tarfile.open(local_filename, 'r') as tar:
                for member in tar.getmembers()[:10]:
                    print('- ' + member.name)
                print('...')

                tar.extractall(str(contents_path))
