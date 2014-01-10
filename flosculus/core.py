import time
from functools import partial

import configparser
from fluent.sender import FluentSender
from fluent import event

from .parser import Parser
from .watcher import LogWatcher


class ConfigError(Exception):
    """An exception class that should be raised when there's
    no exception classes from :module:`configparser` fit
    the context.
    """
    pass


def setup_remote_options(section):
    """Checks remote options if any, otherwise this will set
    default remote options.
    """
    parsed_dict = {
        "remote_host": section.get("remote_host", "localhost"),
        "remote_port": section.get("remote_port", 24224)
    }

    try:
        parsed_dict["remote_port"] = int(parsed_dict["remote_port"])
    except ValueError:
        raise ConfigError(
            "remote_port must be an int; got {!r} instead".format(
                parsed_dict["remote_port"])
        )
    return parsed_dict


def config_from_inifile(inifile):
    """Parses the given any file with `ini` syntax-wise to construct
    necessary configuration values.
    """
    config = configparser.SafeConfigParser()
    config.read(inifile)

    settings = {}
    try:
        settings["flosculus"] = dict(config["flosculus"])
    except KeyError:
        raise configparser.NoSectionError(
            "config file {!r} does not have {!r} section".format(
                inifile, "flosculus")
        )

    # setup global remote options; overridable in log section
    settings["flosculus"].update(
        setup_remote_options(settings["flosculus"]))

    settings["logs"] = {}
    for section, values in config.iteritems():
        if not section.startswith("log:"):
            continue

        path = section.rsplit(":")[1:][0]
        settings["logs"][path] = dict(values)

        # sanity checks for mandatory options
        if "tag" not in settings["logs"][path]:
            raise configparser.NoOptionError("tag", path)
        if "format" not in settings["logs"][path]:
            raise configparser.NoOptionError("format", path)

        remote_opts = setup_remote_options(settings["logs"][path])

        # fallback to global ``remote_host`` option
        remote_opts["remote_host"] = remote_opts.get(
            "remote_host", settings["flosculus"]["remote_host"])

        # fallback to global ``remote_port`` option
        remote_opts["remote_port"] = remote_opts.get(
            "remote_port", settings["flosculus"]["remote_port"])

        settings["logs"][path].update(remote_opts)

    return settings


class Flosculus(object):
    def __init__(self, config):
        self._config = config_from_inifile(config)
        self._watcher = partial(LogWatcher, self._config["logs"].keys())
        self._time_format = "%d/%b/%Y:%H:%M:%S"
        self._routes = {}

        for path, values in self._config["logs"].iteritems():
            tag_parts = values["tag"].strip(".").split(".")
            self._routes[path] = {
                "parser": Parser(values["format"]),
                "sender": FluentSender(
                    tag_parts[0],
                    host=values["remote_host"],
                    port=values["remote_port"],
                ),
                "label": ".".join(tag_parts[1:]),
            }

    def on_recv(self, filename, lines):
        """A callback invoked whenever loop event throws a line
        from a log file.
        """
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
        """Runs the event loop.
        """
        watcher = self._watcher(self.on_recv)
        watcher.loop()
