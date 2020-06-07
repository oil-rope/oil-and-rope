def requests_utils(request):
    host = request.get_host()
    port = request.get_port()
    uri = '{}'.format(host)
    real_uri = request.build_absolute_uri()
    return {
        'host': host,
        'port': port,
        'secure_uri': 'https://{}'.format(uri),
        'insecure_uri': 'http://{}'.format(uri),
        'real_uri': real_uri
    }
