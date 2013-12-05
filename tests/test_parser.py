from flosculus.parser import Parser


def test_parsing_line():
    line = (
        '127.0.0.1 - - [03/Dec/2013:16:29:19 +0700] '
        '"GET /favicon.ico HTTP/1.1" 404 198 '
        '"-" "Mozilla/5.0 (X11; Linux x86_64)" '
    )
    parser = Parser(format_="nginx")
    parsed_line = parser.parse(line)

    # successful operation returns a ``dict``,
    # hence we only need to test the existence and correctness
    # of its key-value pairs
    assert parsed_line["agent"] == "Mozilla/5.0 (X11; Linux x86_64)"


def test_unsupported_format():
    line = '127.0.0.1 - - [03/Dec/2013:16:29:19 +0700]'
    parser = Parser(format_="random_format")

    # failed operation returns a ``None``
    assert parser.parse(line) is None


def test_custom_format():
    line = "127.0.0.1 -"
    parser = Parser(format_='(?P<remote>[^ ]*) (?P<host>[^ ]*)')
    parsed_line = parser.parse(line)

    assert parsed_line["remote"] == "127.0.0.1"
    assert parsed_line["host"] == "-"
