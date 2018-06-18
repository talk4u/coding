from .profile import LangProfile


class Go110(LangProfile, lang_name='go'):
    @property
    def src_file_name(self):
        return 'main.go'

    @property
    def bin_file_name(self):
        return 'main'

    @property
    def version(self):
        return 'Go 1.10.1'

    def builder_image_tag(self, config):
        return config.GO_BUILDER_TAG

    def sandbox_image_tag(self, config):
        return config.NATIVE_SANDBOX_TAG

    def get_compile_cmd(self, src_file, out_file):
        return ['go', 'build', '-o', out_file, src_file]

    def get_exec_cmd(self, bin_file):
        return [bin_file]
