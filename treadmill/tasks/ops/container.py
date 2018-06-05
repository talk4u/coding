from typing import List

import docker
from docker.models.containers import Container

from treadmill.tasks.ops.base import Operation
from treadmill.tasks.path import ROOT


__all__ = [
    'RunDockerContainerOp',
    'ExecInDockerContainerOp',
    'KillDockerContainerOp'
]


docker_client: docker.DockerClient = docker.from_env()


class RunDockerContainerOp(Operation):
    def __init__(self, container_tag, mount_workspace=True, privileged=False):
        self.container_tag = container_tag
        self.mount_workspace = mount_workspace
        self.privileged = privileged

    def _run(self):
        kwargs = dict(
            commands='/bin/sh',  # Assume alpine based image (bash not installed)
            stdin_open=True,     # Keep /bin/sh alive
            remove=True,         # Discard changes made in image after run
            detach=True          # Run in background
        )

        if self.mount_workspace:
            kwargs.update(volumes={
                ROOT.host_path: {
                    'bind': ROOT.container_path,
                    'mode': 'rw'
                }
            })

        if self.privileged:
            kwargs.update(privileged=True)

        return docker_client.containers.run(self.container_tag, **kwargs)


class ExecInDockerContainerOp(Operation):
    def __init__(self, container: Container, cmd: List[str], **kwargs):
        self.container = container
        self.cmd = cmd
        self.kwargs = kwargs

    def _run(self):
        return self.container.exec_run(
            ['/bin/sh', '-c', ' '.join(self.cmd)],
            **self.kwargs
        )


class KillDockerContainerOp(Operation):
    def __init__(self, container: Container):
        self.container = container

    def _run(self):
        if self.container and self.container.status != 'end':
            self.container.kill()
