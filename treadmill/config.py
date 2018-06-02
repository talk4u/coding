import os
from .models import Lang


class TreadmillConfig(object):
    API_ENDPOINT: str
    API_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT = 6537

    SENTRY_DSN = ''

    HOST_WORKSPACE_ROOT: str
    S3FS_ROOT: str

    GCC_BUILDER_TAG = 'talk4u/treadmill-builder-gcc:v0.1.0'
    GO_BUILDER_TAG = 'talk4u/treadmill-builder-go110:v0.1.0'
    JDK_BUILDER_TAG = 'talk4u/treadmill-builder-jdk8:v0.1.0'

    NATIVE_SANDBOX_TAG = 'talk4u/treadmill-sandbox-native:v0.1.0'
    JRE_SANDBOX_TAG = 'talk4u/treadmill-sandbox-jre8:v0.1.0'
    PY3_SANDBOX_TAG = 'talk4u/treadmill-sandbox-py36:v0.1.0'

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


dev_config = TreadmillConfig()
dev_config.API_ENDPOINT = 'http://localhost:8080/api'
dev_config.API_TOKEN = ''
dev_config.REDIS_HOST = 'localhost'
dev_config.HOST_WORKSPACE_ROOT = os.environ['TM_HOST_WORKSPACE_ROOT']
dev_config.S3FS_ROOT = os.environ['TM_S3FS_ROOT']
