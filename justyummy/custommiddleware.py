def print_cookies_middleware(get_response):
    def print_cookies(request):
        print(request.COOKIES)
        return get_response(request)
    return print_cookies