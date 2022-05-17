def requests_utils(request):
    host = request.get_host()
    port = request.get_port()
    uri = '{}'.format(host)
    current_uri = request.build_absolute_uri()
    uri = 'https://{}'.format(uri) if request.is_secure() else 'http://{}'.format(uri)
    return {
        'host': host,
        'port': port,
        'uri': uri,
        'current_uri': current_uri,
    }
