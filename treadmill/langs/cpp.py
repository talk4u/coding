from .profile import LangProfile


class Cpp14(LangProfile, lang_name='cpp'):
    @property
    def src_file_name(self):
        return 'main.cpp'

    @property
    def bin_file_name(self):
        return 'main'

    @property
    def version(self):
        return 'c++14 (g++ 6.4.0)'

    def builder_image_tag(self, config):
        return config.GCC_BUILDER_TAG

    def sandbox_image_tag(self, config):
        return config.NATIVE_SANDBOX_TAG

    def get_compile_cmd(self, src_file, out_file):
        return [
            'g++',
            '-std=c++14',
            '-O2',
            '-o', out_file,
            src_file
        ]

    def get_exec_cmd(self, bin_file, args=()):
        return [bin_file, *args]
