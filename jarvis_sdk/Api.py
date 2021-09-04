"""
Copyright (c) 2021 Philipp Scheer
"""


import requests


class Api():
    BASE_URL = "http://api.jarvis.fipsi.at"

    @staticmethod
    def endpoint(endpoint, post_data={}):
        """Call an endpoint of the official Jarvis API"""
        try:
            result = Api.post(f"{Api.BASE_URL}{endpoint}", post_data=post_data)
        except requests.exceptions.ConnectionError:
            return ApiErrorResponse({}, "API_UNREACHABLE")
        if result.get("success", None):
            return result["result"]
        return ApiErrorResponse(result)

    @staticmethod
    def post(url, post_data={}):
        """Perform a HTTP POST request to given `url` with given `post_data`"""
        return requests.post(url, json=post_data).json()
    
    @staticmethod
    def get(url):
        """Perform a HTTP GET request to given `url`"""
        return requests.get(url).json()


class ApiErrorResponse():
    def __init__(self, raw_response: dict, error_code: str = "UNKNOWN_ERROR") -> None:
        self.r = raw_response
        self.e = error_code
    
    def __bool__(self):
        return False
    
    @property
    def error(self):
        return self.r.get("error", self.r.get("result", self.e))