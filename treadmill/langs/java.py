import os

from .profile import LangProfile


class Java8(LangProfile, lang_name='java'):
    @property
    def src_file_name(self):
        return 'Main.java'

    @property
    def bin_file_name(self):
        return 'Main.class'

    @property
    def version(self):
        return 'OpenJDK 8u151'

    def builder_image_tag(self, config):
        return config.JDK_BUILDER_TAG

    def sandbox_image_tag(self, config):
        return config.JRE_SANDBOX_TAG

    def get_compile_cmd(self, src_file, out_file):
        out_dir = os.path.dirname(out_file)
        return ['javac', '-d', out_dir, src_file]

    def get_exec_cmd(self, bin_file):
        class_path = os.path.dirname(bin_file)
        return [
            '/usr/bin/java',
            '-XX:ParallelGCThreads=1',
            '-Xmx256M',
            '-Xss16M',
            '-cp', class_path,
            'Main'
        ]
