# Imports
from dns import resolver
from flask import Flask, request
from ipaddress import ip_address
from re import split

app = Flask(__name__)


# Get Client Information From Request
def get_client_info(remote: str, forwarded: str, xforwarded: str) -> list:
    client_info: list = ["", True, ""]
    http_via: str = request.headers.get('via')

    if forwarded:
        client_info[0] = split(" ", split(";", forwarded)[0])[-1].lstrip("for=\"[").rstrip("]\"")
        if http_via:
            client_info[2] = split(" ", http_via)[-1]
    elif xforwarded:
        client_info[0] = split(" ", xforwarded)[-1]
        if request.headers.get('via'):
            client_info[2] = split(" ", http_via)[-1]
    elif remote:
        client_info[0] = remote
        client_info[1] = False

    return client_info


@app.route("/")
def my_ip() -> str:
    # Get Client IP, Reverse DNS and Proxy Info
    client_info: list = get_client_info(request.remote_addr, request.headers.get('Forwarded'),
                                        request.headers.get('X-Forwarded-For'))

    if ip_address(client_info[0]).is_global:
        client_ip_reverse_dns: str = split(" IN PTR ",
                                           str(resolver.resolve_address(str(client_info[0])).rrset))[1].rstrip(".")
    else:
        client_ip_reverse_dns: str = ""

    # Format Results To HTML
    if client_info[0]:
        html_client_ip: str = f"<font size=8><br />IP : {client_info[0]}</font>"
    else:
        html_client_ip: str = f"<font size=8><br />IP : No IP Address Found</font>"

    if client_ip_reverse_dns:
        html_client_ip_reverse_dns: str = f"<br /><font size=3><i> Reverse DNS : {client_ip_reverse_dns}</i>"
    else:
        html_client_ip_reverse_dns: str = f"<br /><font size=3><i> Reverse DNS : No Record Found</i>"

    if client_info[1] and client_info[2]:
        html_client_proxy: str = f"""<br /><br /><font size=1>You are using a proxy server<br />Proxy Address : 
                                 {client_info[2]}</font>"""
    elif client_info[1] and not client_info[2]:
        html_client_proxy: str = f"""<br /><br /><font size=1>You are using a proxy server<br />Proxy Address : 
                                 Not Found</font>"""
    else:
        html_client_proxy: str = f"<br /><br /><font size=1>No Proxy detected</font>"

    html: str = f"""<!DOCTYPE html>
<html>
    <head>
        <title>My IP Python Project</title>
        <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
    </head>

    <body>
        <p align="center">
            {html_client_ip}
            {html_client_ip_reverse_dns}
            {html_client_proxy}
        </p>
    </body>
</html>"""
    return html
