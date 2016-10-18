import os
import uuid
import json
import subprocess
from pyroute2 import IPDB, NetNS, netns
from cgroups import Cgroup
from cgroups.user import create_user_cgroups

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
            veth0_name = 'veth0_'+name
            veth1_name = 'veth1_'+name
            netns_name = 'netns_'+name
            bridge_if_name = 'bridge0'

            existing_interfaces = ipdb.interfaces.keys()

            # Create a new virtual interface
            with ipdb.create(kind='veth', ifname=veth0_name, peer=veth1_name) as i1:
                i1.up()
                if bridge_if_name not in existing_interfaces:
                    bridge = ipdb.create(kind='bridge', ifname=bridge_if_name).commit()
                    bridge.add_port(i1)
                else:
                    ipdb.interfaces[bridge_if_name].add_port(i1)

            # Create a network namespace
            netns.create(netns_name)

            # move the bridge interface into the new namespace
            with ipdb.interfaces[veth1_name] as veth1:
                veth1.net_ns_fd = netns_name

            # Use this network namespace as the database
            with IPDB(NetNS(netns_name)) as ns:
                ns.interfaces.lo.up()
                ns.interfaces[veth1_name].address = "02:42:ac:11:00:{0}".format(mac)
                ns.interfaces[veth1_name].add_ip('10.0.0.{0}/24'.format(ip_last_octet))
                ns.interfaces[veth1_name].up()
                ns.routes.add({
                    'dst': 'default',
                    'gateway': '10.0.0.1'})

            try:
                # setup cgroup directory for this user
                user = os.getlogin()
                create_user_cgroups(user)

                # First we create the cgroup and we set it's cpu and memory limits
                cg = Cgroup(name)
                cg.set_cpu_limit(50)  # TODO : get these as command line options
                cg.set_memory_limit(500)

                # Then we a create a function to add a process in the cgroup
                def in_cgroup():
                    pid = os.getpid()
                    cg = Cgroup(name)
                    # Set network namespace
                    netns.setns(netns_name)

                    # Set chroot
                    os.chroot(layer_dir)
                    
                    # add process to cgroup
                    cg.add(pid)

                p2 = subprocess.Popen('echo "hello world" > /tmp/test', preexec_fn=in_cgroup, shell=True)

            except Exception as e:
                log.error(e)
            finally:
                NetNS(netns_name).close()
                netns.remove(netns_name)
                ipdb.interfaces[veth0_name].remove()
