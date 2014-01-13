from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import pytest
from six.moves import configparser

from flosculus.core import config_from_inifile
from flosculus.core import ConfigError
from flosculus.core import Flosculus


def create_inifile(tmpdir, content):
    inifile = tmpdir.mkdir("test_flosculus").join("flosculus.ini")
    inifile.write(content)
    return inifile


def test_config_no_main_section(tmpdir):
    inifile = create_inifile(tmpdir, "[flosc]")
    with pytest.raises(ConfigError):
        config_from_inifile(str(inifile))


def test_config_no_mandatory_log_options(tmpdir):
    inifile = create_inifile(tmpdir, """
[flosculus]
[log:/tmp/dummy.log]
""")
    with pytest.raises(configparser.NoOptionError):
        config_from_inifile(str(inifile))


def test_config_invalid_port(tmpdir):
    inifile = create_inifile(tmpdir, """
[flosculus]
remote_port = abc
""")
    with pytest.raises(ConfigError):
        config_from_inifile(str(inifile))


def test_config_log_section(tmpdir):
    inifile = create_inifile(tmpdir, """
[flosculus]
[log:/tmp/dummy.log]
tag = dummy.example.com
format = nginx
""")
    settings = config_from_inifile(str(inifile))
    assert "logs" in settings


def test_config_global_remote_main_section(tmpdir):
    inifile = create_inifile(tmpdir, """
[flosculus]
""")
    # backward-compat testcase to check deprecated options
    settings = config_from_inifile(str(inifile))
    assert "remote_host" in settings["flosculus"]


def test_config_global_remote_log_section(tmpdir):
    inifile = create_inifile(tmpdir, """
[flosculus]
[log:/tmp/dummy.log]
tag = dummy.example.com
format = nginx
""")
    settings = config_from_inifile(str(inifile))
    assert "remote_host" in settings["logs"]["/tmp/dummy.log"]

    custom_host = settings["logs"]["/tmp/dummy.log"]["remote_host"]
    global_host = settings["flosculus"]["remote_host"]
    assert custom_host == global_host


def test_config_overriden_remote_in_section(tmpdir):
    inifile = create_inifile(tmpdir, """
[flosculus]
[log:/tmp/dummy.log]
tag = dummy.example.com
format = nginx
[log:/tmp/test.log]
tag = test.example.com
format = nginx
remote_port = 24225
""")
    settings = config_from_inifile(str(inifile))
    assert settings["logs"]["/tmp/dummy.log"]["remote_port"] == 24224
    assert settings["logs"]["/tmp/test.log"]["remote_port"] == 24225


def test_flosculus_init(tmpdir):
    inifile = create_inifile(tmpdir, """
[flosculus]
[log:/tmp/dummy.log]
tag = dummy.example.com.
format = nginx
[log:/tmp/example.log]
tag = test.example.com
format = nginx
remote_port = 24225
""")

    fl = Flosculus(str(inifile))
    assert fl._routes["/tmp/dummy.log"]["sender"].port == 24224
    assert fl._routes["/tmp/dummy.log"]["sender"].tag == "dummy"
    assert fl._routes["/tmp/dummy.log"]["label"] == "example.com"
    assert fl._routes["/tmp/example.log"]["sender"].port == 24225
