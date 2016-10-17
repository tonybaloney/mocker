import requests
import os
import json
from mocker import _base_dir_
from .base import BaseDockerCommand


class PullCommand(BaseDockerCommand):
    def run(self, *args, **kwargs):
        image = kwargs['<name>']
        library = 'library' # todo - user-defined libraries
        tag = kwargs['<tag>'] if kwargs['<tag>'] is not None else 'latest'
        headers = {'X-Docker-Token': True}

        # request a v2 token
        token_req = requests.get(
            'https://auth.docker.io/token?service=registry.docker.io&scope=repository:%s/%s:pull'
            % (library, image))
        token_response = token_req.json()
        headers = {
            'Authorization': 'Bearer %s' % token_response['token']}

        # get the image manifest
        registry_base = 'https://registry-1.docker.io/v2'
        print("Fetching manifest for %s:%s..." % (image, tag))

        manifest = requests.get('%s/%s/%s/manifests/%s' %
                                (registry_base, library, image, tag),
                                headers=headers)

        manifest = manifest.json()

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
        for sig in unique_layer_sigs:
            print('Fetching layer %s..' % sig)
            url = '%s/%s/%s/blobs/%s' % (registry_base, library, image, sig)
            local_filename = os.path.join(dl_path, sig) + '.tar'

            r = requests.get(url, stream=True, headers=headers)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
