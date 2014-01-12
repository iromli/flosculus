Flosculus
=========

Flosculus is a **work-in-progress** script to tail rotated log file, parse each line, and send it to Fluentd.
It is intended to replace a subset of Fluentd ``in_tail`` features.

Crash Course
------------

First things first, install Flosculus into your Python path.

.. code-block:: sh

    $ git clone git://github.com/iromli/flosculus.git
    $ cd flosculus
    $ python setup.py install

Afterwards you need to create a configuration file to run the ``flosculusd`` event loop.
The convenient way to do this boring thing is by invoking the ``flosculusd --init > flosculus.ini`` command.
Here's an example of ``flosculus.ini`` (you can call it whatever you like):

.. code-block:: ini

    [flosculus]
    ; the IP address (or host name) of the remote server
    remote_host = 127.0.0.1

    ; the TCP port of the remote server
    remote_port = 24224


    ; Each section with `path:/path/to/log` is a valid config
    [log:/var/log/nginx/access.log]

    ; the label
    tag = example.api.access

    ; format to use, either use 'nginx' or custom regex
    format = nginx

By default, the ``format`` option is matched against **nginx** default access log format.
You may change the format as long as using a valid Python regex.

.. code-block:: ini

    [log:/var/log/nginx/access.log]

    format = (?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] "(?P<method>\S+)(?: +(?P<path>[^\"]*) +\S*)?" (?P<code>[^ ]*) (?P<size>[^ ]*)(?: "(?P<referer>[^\"]*)" "(?P<agent>[^\"]*)")(?: (?P<request_time>[^ ]*) (?P<upstream_time>[^ ]*) (?P<pipe>[\.|p]))?

And did I already mentioned that you can have multiple log files? Simply copy the whole ``log`` section.

.. code-block:: ini

    ; Each section with `path:/path/to/log` is a valid config
    [log:/var/log/nginx/access.log]

    ; the label
    tag = example.api.access

    ; format to use, either use 'nginx' or custom regex
    format = nginx

    ; Each section with `path:/path/to/log` is a valid config
    [log:/var/log/nginx/timed-combined.access.log]

    ; the label
    tag = test.api.access

    ; format to use, either use 'nginx' or custom regex
    format = (?P<remote>[^ ]*) (?P<host>[^ ]*) (?P<user>[^ ]*) \[(?P<time>[^\]]*)\] "(?P<method>\S+)(?: +(?P<path>[^\"]*) +\S*)?" (?P<code>[^ ]*) (?P<size>[^ ]*)(?: "(?P<referer>[^\"]*)" "(?P<agent>[^\"]*)")(?: (?P<request_time>[^ ]*) (?P<upstream_time>[^ ]*) (?P<pipe>[\.|p]))?

    ; the IP address (or host name) of the remote server
    ; use another Fluentd remote host
    remote_host = 10.0.0.1

    ; the TCP port of the remote server
    ; use another Fluentd remote port
    remote_port = 24225

Assuming the configuration is written properly, run the event loop to see its magic (well, not really):

.. code-block:: sh

    $ flosculusd -c flosculus.ini

Credits
-------

* `Beaver <https://github.com/josegonzalez/beaver>`_
* `Fluentd <https://github.com/fluent/fluentd>`_
