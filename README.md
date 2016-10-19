# mocker
A proof-of-concept imitation of Docker, written in 100% Python. Using Kernel Namespaces, cgroups and network namespaces/iproute2 for Linux.

![](https://pbs.twimg.com/media/CmE8k1qVAAAZrIt.jpg)

## Why?

I keep hearing statements like "Docker is basically just cgroups", "Docker is just chroot on steroids", which is totally incorrect.

I'm giving a talk at the Sydney Docker meetup on the 18th October about some of the core concepts in Kernel namespaces, cgroups and network namespaces and fancied a simple implementation to show how container isolation works, the docker image format (the new API) and also how much more there is to
Docker than those core kernel features.

## Caveats

1. I wrote this in 2 days, don't take it seriously
2. This will only work on Linux, tested on CentOS 7 and Ubuntu 14. 
3. Try out the nginx container ![](https://pbs.twimg.com/media/CvEzEJFUIAQfX2z.jpg)
4. My networking implementation is half-finished, still need to figure out the NAT'ing.
5. I tried some images and had problems with their start commands, I must be layering the stack incorrectly. It does chroot on the squashed image download instead of using a btrfs snapshot mount. 

## mocker pull

Mocker pull will download a Docker image from the Docker public repository, download the image layers and extract them into a local folder.

```
./mocker.py pull hello-world
Starting new HTTPS connection (1): auth.docker.io
Setting read timeout to None
"GET /token?service=registry.docker.io&scope=repository:library/hello-world:pull HTTP/1.1" 200 1450
Fetching manifest for hello-world:latest...
Starting new HTTPS connection (1): registry-1.docker.io
Setting read timeout to None
"GET /v2/library/hello-world/manifests/latest HTTP/1.1" 200 2750
Fetching layer sha256:c04b14da8d1441880ed3fe6106fb2cc6fa1c9661846ac0266b8a5ec8edf37b7c..
Starting new HTTPS connection (1): registry-1.docker.io
Setting read timeout to <object object at 0x7fabadba50b0>
"GET /v2/library/hello-world/blobs/sha256:c04b14da8d1441880ed3fe6106fb2cc6fa1c9661846ac0266b8a5ec8edf37b7c HTTP/1.1" 307 432
Starting new HTTPS connection (1): dseasb33srnrn.cloudfront.net
Setting read timeout to <object object at 0x7fabadba50b0>
"GET /registry-v2/docker/registry/v2/blobs/sha256/c0/c04b14da8d1441880ed3fe6106fb2cc6fa1c9661846ac0266b8a5ec8edf37b7c/data?Expires=1476758515&Signature=P~1JaRJM6u9SNOq9c8MTsie5cEN4HPixwAKza2FPGnXu85au4r0fcbUhRWFnENHyTR1ntlYajARBIbelKb4Yf92OTFyVum~hKmOs3fXz7dCTRLNQDJ6iCuGZG1apqQ7j4JJLqP8bnkIe40FZ6WbYxG3pYqv2s0lxsdsFytgvCm0_&Key-Pair-Id=APKAJECH5M7VWIS5YZ6Q HTTP/1.1" 200 974
- hello
...
Fetching layer sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4..
Starting new HTTPS connection (1): registry-1.docker.io
Setting read timeout to <object object at 0x7fabadba50b0>
"GET /v2/library/hello-world/blobs/sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4 HTTP/1.1" 307 432
Starting new HTTPS connection (1): dseasb33srnrn.cloudfront.net
Setting read timeout to <object object at 0x7fabadba50b0>
"GET /registry-v2/docker/registry/v2/blobs/sha256/a3/a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4/data?Expires=1476758516&Signature=CkRP6ohZMxL5OJ5pX9Oamsds5oP8AEafk0otQo4Udd21DA5SparSxSlJSR7JxXkF16BS8X2kdbVGxdJxehNHCsvb~Z2dIVyA9Vrr6XKgAfmgfP2prt2GixMJzi0HZDut8DRgSK57qlzvGlYRmeKL-pk5q1HCEEgwmHoTnW450NY_&Key-Pair-Id=APKAJECH5M7VWIS5YZ6Q HTTP/1.1" 200 32
...
```

## mocker image

Mocker images will show you which images you've already downloaded

```
./mocker.py images
+------------------+---------+----------+-----------------------+
| name             | version | size     | file                  |
+------------------+---------+----------+-----------------------+
| library/tomcat   | latest  | 153.9MiB | library_tomcat.json   |
| library/rabbitmq | latest  | 82.6MiB  | library_rabbitmq.json |
+------------------+---------+----------+-----------------------+
```

## mocker run

Mocker run will

- Create a veth0 bridge virtual ethernet adapter in the root namespace
- Create a network namespace for the "container"
- Bridge a veth1 adapter into the new network namespace under the IP 10.0.0.3/24
- Setup a default route for 10.0.0.1
- Create a cgroup for the processes
- ChRoot to the extracted image directory - no snapshots (yet) which is bad
- Execute the docker image's chosen Cmd, setup environment variables and write the output to /tmp/stdout

```
./mocker.py run library/hello-world
Creating cgroups sub-directories for user root
Hierarchies availables: ['hugetlb', 'perf_event', 'blkio', 'devices', 'memory', 'cpuacct', 'cpu', 'cpuset', 'freezer', 'systemd']
cgroups sub-directories created for user root
Creating cgroups sub-directories for user root
Hierarchies availables: ['hugetlb', 'perf_event', 'blkio', 'devices', 'memory', 'cpuacct', 'cpu', 'cpuset', 'freezer', 'systemd']
cgroups sub-directories created for user root
Running "/hello"
Creating cgroups sub-directories for user root
Hierarchies availables: ['hugetlb', 'perf_event', 'blkio', 'devices', 'memory', 'cpuacct', 'cpu', 'cpuset', 'freezer', 'systemd']
cgroups sub-directories created for user root
Setting ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker Hub account:
 https://hub.docker.com

For more examples and ideas, visit:
 https://docs.docker.com/engine/userguide/

None
None
Finalizing
done
```

## TODO

The other 99.999% of Docker. I only had 2 days to write this!
