import logging


class IndentLogger(logging.Logger):
    _indent_provider = None

    def set_indent_provider(self, indent_provider):
        self._indent_provider = indent_provider

    def debug_with_indent(self, message):
        indent = self._indent_provider()
        self.debug(indent + str(message))


logging.setLoggerClass(IndentLogger)
