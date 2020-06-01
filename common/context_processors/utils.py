def requests_utils(request):
    host = request.get_host()
    port = request.get_port()
    raw_uri = 'https://' if request.is_secure() else 'http://'
    raw_uri = '{}{}'.format(raw_uri, host)
    return {
        'host': host,
        'port': port,
        'raw_uri': raw_uri
    }
