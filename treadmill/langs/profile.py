from abc import ABC, abstractmethod


class LangProfile(ABC):
    __all_profiles = {}
    _instance = None

    def __init_subclass__(cls, **kwargs):
        if 'lang_name' not in kwargs:
            raise TypeError('Must specify lang_name when subclassing LangProfile')
        name = kwargs.pop('lang_name')
        LangProfile.__all_profiles[name] = cls

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_profile(cls, lang):
        return cls.__all_profiles.get(lang.name.lower()).instance()

    @property
    @abstractmethod
    def src_file_name(self):
        pass

    @property
    @abstractmethod
    def bin_file_name(self):
        pass

    @property
    @abstractmethod
    def version(self):
        pass

    @abstractmethod
    def builder_image_tag(self, config):
        pass

    @abstractmethod
    def sandbox_image_tag(self, config):
        pass

    @property
    def need_compile(self):
        return True

    @abstractmethod
    def get_compile_cmd(self, src_file, out_file):
        pass

    @abstractmethod
    def get_exec_cmd(self, bin_file):
        pass
