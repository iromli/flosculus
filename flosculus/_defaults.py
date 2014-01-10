DEFAULT_CONFIG = """
[flosculus]
; the IP address (or host name) of the remote server
; this is a global option but it's easily overriden in log section
remote_host = 127.0.0.1

; the TCP port of the remote server
; this is a global option but it's easily overriden in log section
remote_port = 24224


; Each section with `path:/path/to/log` is a valid config
[log:/var/log/nginx/access.log]

; the label
tag = example.api.access

; format to use, either use 'nginx' or custom regex
format = nginx

; the IP address (or host name) of the remote server
; uncomment this option if you want to use custom remote host
; for current log
;remote_host = 127.0.0.1

; the TCP port of the remote server
; uncomment this option if you want to use custom remote port
; for current log
;remote_port = 24224
"""
