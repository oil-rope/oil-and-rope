from django.http.request import HttpRequest


def requests_utils(request: HttpRequest):
    scheme = request.scheme or 'https'
    host = request.get_host()
    port = request.get_port()
    uri = request.build_absolute_uri()

    return {
        'scheme': scheme,
        'host': host,
        'port': port,
        'uri': uri,
    }
