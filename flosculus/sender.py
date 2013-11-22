import re
import time

from fluent import sender as fluent_sender
from fluent import event

from .parser import Parser


class Sender(object):
    def __init__(self, tag, **kwargs):
        tag_parts = tag.split(".")

        fluent_sender.setup(tag_parts[0], **kwargs)
        self._label = ".".join(tag_parts[1:])

        self._parser = Parser(kwargs.get("format"))
        self._time_format = "%d/%b/%Y:%H:%M:%S"

    def on_log_parsed(self, filename, lines):
        # TODO: use generator
        for line in lines:
            parsed_line = self._parser.parse(line)

            if not parsed_line:
                continue

            ts = time.strptime(
                parsed_line["time"].split()[0], self._time_format)
            event.Event(
                self._label, parsed_line, time=int(time.mktime(ts)))
