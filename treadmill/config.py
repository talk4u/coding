from .models import Lang


class TreadmillConfig(object):
    API_ENDPOINT: str
    API_TOKEN: str

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
        elif lang == Lang:
            return cls.JRE_SANDBOX_TAG
        elif lang == Lang.PYTHON3:
            return cls.PY3_SANDBOX_TAG


class LocalConfig(TreadmillConfig):
    API_ENDPOINT = 'http://localhost:8080/api'
    API_TOKEN = ''

    HOST_WORKSPACE_ROOT = '~/Temp/treadmill/workspace'
    S3FS_ROOT = '~/mnt/talk4u-data'
