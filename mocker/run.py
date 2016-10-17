import os
import uuid
import json
import subprocess

from cgroups import Cgroup

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
        with open(target_file) as tf:
            image_details = json.loads(tf.read())

        name = 'container_' + str(uuid.uuid1()).replace('-', '_')

        layer_dir = os.path.join(_base_dir_, match.replace('.json', ''), 'layers', 'contents')

        net_commands = """
        ip link add dev veth0_{0} type veth peer name veth1_{0}
        ip link set dev veth0_{0} up
        ip link set veth0_{0} master bridge0
        ip netns add netns_{0}
        ip link set veth1_{0} netns netns_{0}
        ip netns exec netns_{0} ip link set dev lo up
        ip netns exec netns_{0} ip link set veth1_{0} address 02:42:ac:11:00{2}
        ip netns exec netns_{0} ip addr add 10.0.0.{1}/24 dev veth1_{0}
        ip netns exec netns_{0} ip link set dev veth1_{0} up
        ip netns exec netns_{0} ip route add default via 10.0.0.1"""
        for command in net_commands.split('\n'):
            # TODO: make IP configurable
            command_str = command.format(name, 3, ':33')
            out = subprocess.check_output(command_str)
            if not out:
                raise RuntimeError("Arrrrrghhh")

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
