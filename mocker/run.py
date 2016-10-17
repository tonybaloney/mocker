import os
import uuid
import json
import subprocess
from pyroute2 import IPDB, NetNS, netns, IPRoute
from cgroups import Cgroup

from mocker import _base_dir_, log
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
        ip_last_octet = 3 # TODO : configurable

        match = [i[3] for i in images if i[0] == image_name][0]

        target_file = os.path.join(_base_dir_, match)
        with open(target_file) as tf:
            image_details = json.loads(tf.read())
        id = uuid.uuid1()

        # unique-ish name
        name = 'c_' + str(id.fields[5])[:4]

        # unique-ish mac
        mac = str(id.fields[5])[:2]

        layer_dir = os.path.join(_base_dir_, match.replace('.json', ''), 'layers', 'contents')

        with IPDB() as ipdb:
            log.debug(ip.get_links())
            veth_name = 'veth_'+name
            netns_name = 'netns_'+name
            # Create a new virtual interface
            i1 = ipdb.create(kind='veth', ifname=veth_name, peer=veth_name).commit()
            i1.up()

            bridge = ipdb.create(kind='bridge', ifname='bridge0')
            bridge.add_port(i1)
            net_commands = "ip netns exec netns_{0} ip route add default via 10.0.0.1"

            netns.create(netns_name)
            i1.net_ns_fd = netns_name
            with NetNS(netns_name) as ns:
                ns.interfaces.lo.up()
                ns.interfaces[veth_name].address = "02:42:ac:11:00:{0}".format(mac)
                ns.interfaces[veth_name].add_ip('10.0.0.{0}/24'.format(ip_last_octet))
                ns.interfaces[veth_name].up()

            # First we create the cgroup and we set it's cpu and memory limits
            cg = Cgroup(name)
            cg.set_cpu_limit(50)  # TODO : get these as command line options
            cg.set_memory_limit(500)

            # Then we a create a function to add a process in the cgroup
            def in_cgroup():
                pid = os.getpid()
                cg = Cgroup(name)
                cg.add(pid)

            with Chroot(layer_dir):
                entry_cmd = '/bin/sh echo "gordo!"' # TODO get out of Dockerfile
                p1 = subprocess.Popen(entry_cmd, preexec_fn=in_cgroup)
                p1.wait()
                print(p1.stdout)

            i1.release()
            NetNS(netns_name).close()
