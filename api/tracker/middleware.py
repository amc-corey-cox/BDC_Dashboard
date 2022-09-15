import re

class CustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        #This will need to be updated if WSGIServer is updated
        response['Server'] = "WSGIServer/0.2"
        return response