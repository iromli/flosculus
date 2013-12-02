DEFAULT_CONFIG = """
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
"""
