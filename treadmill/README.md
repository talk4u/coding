# Treadmill

Sandbox untrusted code runner.

> **NOTE**: This project uses separate requirements.txt.

## How to Run

### Requirements

To run treadmill worker locally, you need to setup followings:

- Docker should be installed
- Build (or fetch) treadmill docker images using `treadmill/dockers/build.sh` script
- Run s3fs to mount S3 bucket into your local directory (add your mounted directory to environment variable `S3FS_ROOT`)
- Prepare local workspace directory that will be shared through docker container (default: `~/Temp/treadmill/workspace` or use environment variable `HOST_WORKSPACE_ROOT`)
- You need a running redis server at localhost:6537 (favorably through docker)
- Install `treadmill/requirements.txt` in your virtualenv


### Run Treadmill worker

After the requirements has been met, you can run treadmill worker using dramatiq utility

``` shell
> dramatiq treadmill/worker --config LocalConfig
```

## Development Guideline

### Model definition using `DataClass`

We use [`marshmallow`](http://marshmallow.readthedocs.io/) to deserialize JSON string into
`DataClass` python object. `DataClass` uses type annotation to automatically define
marshmallow schema, so all you need to do is defining python class like `typing.NamedTuple`:

``` python
class Person(DataClass):
  first_name: str
  last_name: str
  age: int = 25

  @property
  def name(self):
    return 'f{self.fist_name} {self.last_name}'

if __name__ == '__main__':
  print(Person.schema().loads('{"first_name": "Jongbin", "last_name": "Park"}')
  # Will return Person(first_name="Jongbin", last_name="Park", age=25)
  print(Person.schema().dumps(Person(first_name="Seungyong", last_name="Lee"))
  # Will print {"first_name": "Jongbin", "last_name": "Park", "age": 25}
```

### Task definition

Treadmill worker runs single task called `TreadmillJudgeTask` which consists of multiple
other tasks that inherits `SimpleTask` or `ContextTask`. All tasks under single parent task
share the same `JudgeContext`, and running subtasks requires the caller to explicitly
pass it's own context in argument like:

``` python
class ParentTask(SimpleTask):
  def _run_impl(self):
    ChildTask('Jongbin').run(self.context)  # pass self.context when run()

class ChildTask(SimpleTask):
  def __init__(self, name):
    self.name = name

  def _run_impl(self):
    print(f'Hello, {self.name}')
```

`ContextTask` is useful when you need to cleanup after running all the subtasks and can
be used with `with` clause.

``` python
class DockerContext(ContextTask):
  def _enter(self):
    self.container = docker.containers.run()

  def _exit(self):
    if self.container:
      self.container.kill()

class RunTask(SimpleTask):
  def _run_impl(self):
    with DockerContext().run(self.context) as dc:
      dc.container.exec_run('echo "hello world"')
```


### Dramatiq

`JudgeRequest` message enqueueing and processing is done via (`dramatiq`)[dramatiq.io].
To enqueue message, use dramatiq actor definition in `treadmill/worker.py`. Reference
dramatiq documentation for further usage detail.

``` python
import json
from treadmill.worker import WorkerFactory

factory = WorkerFactory(config)
judge_worker = factory.judge_worker()
judge_worker.send(json.dumps({
  'id': 42,
  'submission_id': 40,
  'rejudge': False
})
```
