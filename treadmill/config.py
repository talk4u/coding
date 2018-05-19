from .models import Lang


class TreadmillConfig(object):
    HOST_WORKSPACE_ROOT = '~/Temp/treadmill/workspace'
    S3FS_ROOT = '~/mnt/talk4u-data'

    GCC_BUILDER_TAG = 'talk4u/treadmill-builder-gcc:v0.1.0'
    GO_BUILDER_TAG = 'talk4u/treadmill-builder-go110:v0.1.0'
    JDK_BUILDER_TAG = 'talk4u/treadmill-builder-jdk8:v0.1.0'

    NATIVE_SANDBOX_TAG = 'talk4u/treadmill-sandbox-native:v0.1.0'
    JRE_SANDBOX_TAG = 'talk4u/treadmill-sandbox-jre8:v0.1.0'
    PY3_SANDBOX_TAG = 'talk4u/treadmill-sandbox-py36:v0.1.0'

    @classmethod
    def builder_container_tag(cls, lang_profile):
        if lang_profile == Lang.CPP:
            return cls.GCC_BUILDER_TAG
        elif lang_profile == Lang.JAVA:
            return cls.JDK_BUILDER_TAG
        elif lang_profile == Lang.GO:
            return cls.GO_BUILDER_TAG

    @classmethod
    def sandbox_container_tag(cls, lang_profile):
        if (lang_profile == Lang.CPP or
                lang_profile == Lang.GO):
            return cls.NATIVE_SANDBOX_TAG
        elif lang_profile == Lang:
            return cls.JRE_SANDBOX_TAG
        elif lang_profile == Lang.PYTHON3:
            return cls.PY3_SANDBOX_TAG
