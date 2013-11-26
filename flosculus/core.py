import time
from functools import partial

from fluent.sender import FluentSender
from fluent import event

from .parser import Parser
from .watcher import LogWatcher


class ConfigError(Exception):
    pass


class Flosculus(object):
    def __init__(self, config):
        logs = {
            val["path"]: val for key, val in config.iteritems()
            if key not in ("DEFAULT", "flosculus",)
        }
        files = [path for path in logs]

        self._watcher = partial(LogWatcher, files)
        self._time_format = "%d/%b/%Y:%H:%M:%S"
        self._routes = {}

        url_parts = config["flosculus"]["fluent_url"].split(":")
        try:
            host, port = url_parts[0], int(url_parts[1])
        except IndexError:
            host, port = url_parts[0], 24224
        except ValueError:
            raise ConfigError(
                "port must be an integer: {!r}".format(url_parts[1]))

        for path, section in logs.iteritems():
            tag_parts = section["tag"].split(".")
            self._routes[path] = {
                "parser": Parser(section["format"]),
                "sender": FluentSender(
                    tag_parts[0], host=host, port=port),
                "label": ".".join(tag_parts[1:]),
            }

    def on_recv(self, filename, lines):
        for line in iter(lines):
            route = self._routes.get(filename)
            if not route:
                continue

            parsed_line = route["parser"].parse(line)

            if not parsed_line:
                continue

            ts = time.strptime(
                parsed_line["time"].split()[0], self._time_format)

            event.Event(
                route["label"],
                parsed_line,
                time=int(time.mktime(ts)),
                sender=route["sender"],
            )

    def run(self):
        watcher = self._watcher(self.on_recv)
        watcher.loop()
