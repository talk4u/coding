import pytest


def assert_finished(gen, send=None):
    try:
        gen.send(send)
        pytest.fail('Generator not finished')
    except StopIteration as e:
        return e.value


def assert_props(obj, expected_type, **expected_props):
    assert isinstance(obj, expected_type)
    for prop_name, prop_val  in expected_props.items():
        assert getattr(obj, prop_name) == prop_val


def run_generator_with_inputs(gen, inputs):
    inputs = [None] + inputs
    results = [gen.send(value) for value in inputs[:-1]]
    results.append(assert_finished(gen, inputs[-1]))
    return results


class Wrap(object):
    def __init__(self, inner):
        self._inner = inner

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def setup(self, results=None):
        if results is None:
            return self._setup()
        return run_generator_with_inputs(self._setup(), results)

    def teardown(self, results=None):
        if results is None:
            return self._teardown()
        return run_generator_with_inputs(self._teardown(), results)

    def run(self, results=None):
        if results is None:
            return self._run()
        return run_generator_with_inputs(self._run(), results)
