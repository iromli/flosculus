import configparser
import pytest

from flosculus.core import config_from_inifile
from flosculus.core import ConfigError


def create_inifile(tmpdir, content):
    inifile = tmpdir.mkdir("test_flosculus").join("flosculus.ini")
    inifile.write(content)
    return inifile


def test_config_main_section(tmpdir):
    inifile = create_inifile(tmpdir, "[flosculus]")
    settings = config_from_inifile(str(inifile))
    assert "flosculus" in settings


def test_config_no_main_section(tmpdir):
    inifile = create_inifile(tmpdir, "[flosc]")
    with pytest.raises(configparser.NoSectionError):
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
""")
    settings = config_from_inifile(str(inifile))
    assert "logs" in settings
