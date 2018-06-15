from .profile import LangProfile


class Python36(LangProfile, lang_name='python3'):
    @property
    def src_file_name(self):
        return 'main.py'

    @property
    def bin_file_name(self):
        return 'main.pyc'

    @property
    def version(self):
        return 'Python 3.6.5'

    def builder_image_tag(self, config):
        return config.PY3_SANDBOX_TAG

    def sandbox_image_tag(self, config):
        return config.PY3_SANDBOX_TAG

    def get_compile_cmd(self, src_file, out_file):
        return ['/usr/local/bin/python', '-m', 'py_compile', src_file]

    def get_exec_cmd(self, bin_file):
        return ['/usr/local/bin/python', bin_file]
