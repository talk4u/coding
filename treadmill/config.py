import os
from .models import Lang


class BaseConfig(object):
    API_ENDPOINT: str = None
    API_SECRET_KEY: str = None

    REDIS_HOST: str = None
    REDIS_PORT: int = 6379

    SENTRY_DSN: str = None

    HOST_WORKSPACE_ROOT: str = None
    S3FS_ROOT: str = None

    GCC_BUILDER_TAG = 'talk4u/treadmill-builder-gcc:v0.1.0'
    GO_BUILDER_TAG = 'talk4u/treadmill-builder-go110:v0.1.0'
    JDK_BUILDER_TAG = 'talk4u/treadmill-builder-jdk8:v0.1.0'

    NATIVE_SANDBOX_TAG = 'talk4u/treadmill-sandbox-native:v0.1.0'
    JRE_SANDBOX_TAG = 'talk4u/treadmill-sandbox-jre8:v0.1.0'
    PY3_SANDBOX_TAG = 'talk4u/treadmill-sandbox-py36:v0.1.0'

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _set_prop(self, key, kwargs):
        if key in kwargs:
            setattr(self, key, kwargs.pop(key))
        else:
            setattr(self, key, os.environ['TM_' + key])

    @classmethod
    def builder_container_tag(cls, lang):
        if lang == Lang.CPP:
            return cls.GCC_BUILDER_TAG
        elif lang == Lang.JAVA:
            return cls.JDK_BUILDER_TAG
        elif lang == Lang.GO:
            return cls.GO_BUILDER_TAG

    @classmethod
    def sandbox_container_tag(cls, lang):
        if lang == Lang.CPP or lang == Lang.GO:
            return cls.NATIVE_SANDBOX_TAG
        elif lang == Lang.JAVA:
            return cls.JRE_SANDBOX_TAG
        elif lang == Lang.PYTHON3:
            return cls.PY3_SANDBOX_TAG


class DevConfig(BaseConfig):
    API_ENDPOINT = 'http://localhost:8000/api'
    API_SECRET_KEY = '!s!5w=_1)(0s*ain9(z125yj3sb2-cf6%g1!9njt^f+u)l9%8*'
    REDIS_HOST = 'localhost'

    def __init__(self, **kwargs):
        self._set_prop('HOST_WORKSPACE_ROOT', kwargs)
        self._set_prop('S3FS_ROOT', kwargs)
        super().__init__(**kwargs)


class TestConfig(BaseConfig):
    pass
