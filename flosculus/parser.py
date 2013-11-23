import logging
import re
import logbook

logger = logbook.Logger(__name__)


DEFAULT_FORMAT_CHOICES = {
    "nginx": (
        '(?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) '
        '\[(?P<time>[^\]]*)\] "(?P<method>\S+)(?: +(?P<path>[^\"]*) +\S*)?" '
        '(?P<code>[^ ]*) (?P<size>[^ ]*)'
        '(?: "(?P<referer>[^\"]*)" "(?P<agent>[^\"]*)")'
    ),
}


class Parser(object):
    def __init__(self, format_):
        if format_ in DEFAULT_FORMAT_CHOICES:
            self._format = DEFAULT_FORMAT_CHOICES.get(format_)
        else:
            self._format = format_

        self._keys = re.findall("\?P<(.*?)>", self._format)
        self._line_re = re.compile(self._format)

    def parse(self, line):
        pattern = self._line_re.search(line)
        try:
            return dict(zip(self._keys, pattern.groups()))
        except AttributeError as exc:
            logger.warn("line doesn't match the format '%s'" % self._format)
            return