def get_moredeals_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise ValueError("Authorization header is missing")
    return auth_header
