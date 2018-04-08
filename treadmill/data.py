import os

from treadmill.models import LanguageProfile


class LanguageProfileData(object):
    def __init__(self, *,
                 src_file_name,
                 bin_naming_rule):
        self.src_file_name = src_file_name
        self._bin_naming_rule = bin_naming_rule
        self.src_bin_name = bin_naming_rule(os.path.basename(src_file_name))

    def get_bin_name(self, src_basename):
        return self._bin_naming_rule(src_basename)


LANG_PROFILES = {
    LanguageProfile.cpp: LanguageProfileData(
        src_file_name='main.cpp',
        bin_naming_rule=lambda basename: basename
    ),
    LanguageProfile.java: LanguageProfileData(
        src_file_name='Main.java',
        bin_naming_rule=lambda basename: basename + '.class'
    ),
    LanguageProfile.python3: LanguageProfileData(
        src_file_name='main.py',
        bin_naming_rule=lambda basename: basename + '.py'
    ),
    LanguageProfile.go: LanguageProfileData(
        src_file_name='main.go',
        bin_naming_rule=lambda basename: basename
    )
}
